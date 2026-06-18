import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType
import numpy as np

import sys
import onnxruntime.quantization.quant_utils as quant_utils

# Patch load_model_with_shape_infer to avoid WinError 32 PermissionError on Windows
def patched_load_model_with_shape_infer(model_path):
    import onnx
    from pathlib import Path
    inferred_model_path = quant_utils.generate_identified_filename(Path(model_path), "-inferred")
    onnx.shape_inference.infer_shapes_path(str(model_path), str(inferred_model_path))
    model = onnx.load(inferred_model_path.as_posix())
    quant_utils.add_infer_metadata(model)
    try:
        inferred_model_path.unlink()
    except PermissionError:
        pass # Ignore permission error on Windows
    return model

quant_utils.load_model_with_shape_infer = patched_load_model_with_shape_infer
if 'onnxruntime.quantization.quantize' in sys.modules:
    sys.modules['onnxruntime.quantization.quantize'].load_model_with_shape_infer = patched_load_model_with_shape_infer

model_id = 'intfloat/multilingual-e5-small'

tokenizer = AutoTokenizer.from_pretrained(model_id)
base_model = AutoModel.from_pretrained(model_id)

tokenizer.save_pretrained('./sbert_tokenizer')

class SBERTPooler(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.base_model = base_model
        
    def forward(self, input_ids, attention_mask):
        outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
        token_embeddings = outputs.last_hidden_state
        
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        embeddings = sum_embeddings / sum_mask
        
        # L2 normalization
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings

model = SBERTPooler(base_model)
model.eval()

dummy_text = 'Ini adalah contoh kalimat untuk diekstrak menjadi vektor.'
dummy_input = tokenizer(dummy_text, return_tensors='pt')
dummy_input

onnx_model_path = 'onnx_SBERT/sbert_embedding.onnx'

torch.onnx.export(
    model,
    (dummy_input['input_ids'], dummy_input['attention_mask']),
    onnx_model_path,
    input_names=['input_ids', 'attention_mask'],
    output_names=['embeddings'],
    dynamic_axes={'input_ids': {0: 'batch_size', 1: 'sequence_length'},
                  'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
                  'embeddings': {0: 'batch_size'}},
    opset_version=14,
    do_constant_folding=True
)
print(f'Model exported to {onnx_model_path}')

quantized_model_path = 'onnx_SBERT/sbert_embedding_quantized.onnx'

quantize_dynamic(
    onnx_model_path,
    quantized_model_path,
    weight_type=QuantType.QUInt8
)
print(f'Quantized model exported to {quantized_model_path}')

session = ort.InferenceSession(quantized_model_path)
inputs = {
    'input_ids': dummy_input['input_ids'].numpy(),
    'attention_mask': dummy_input['attention_mask'].numpy()
}
outputs = session.run(None, inputs)

print('Embeddings shape:', outputs[0].shape)
print('Sample embeddings:', outputs[0][0][:5])
