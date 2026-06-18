import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType
import numpy as np
import os

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

model_id = 'dslim/bert-base-NER'

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForTokenClassification.from_pretrained(model_id)
model.eval()

tokenizer.save_pretrained('./ner_tokenizer')

dummy_text = 'John Doe lives in New York and works as an Engineer.'
dummy_input = tokenizer(dummy_text, return_tensors='pt')
dummy_input

onnx_model_path = 'onnx_NER/ner_model.onnx'

torch.onnx.export(
    model,
    (dummy_input['input_ids'], dummy_input['attention_mask']),
    onnx_model_path,
    input_names=['input_ids', 'attention_mask'],
    output_names=['logits'],
    dynamic_axes={'input_ids': {0: 'batch_size', 1: 'sequence_length'},
                  'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
                  'logits': {0: 'batch_size', 1: 'sequence_length'}},
    opset_version=14,
    do_constant_folding=True
)
print(f'Model exported to {onnx_model_path}')

quantized_model_path = 'onnx_NER/ner_model_quantized.onnx'

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

print('Logits shape:', outputs[0].shape)

predicted_ids = np.argmax(outputs[0], axis=-1)
print('Predicted tokens:', [tokenizer.decode(t) for t in predicted_ids[0]])

# Memetakan prediksi ke label entitas
labels = model.config.id2label
predicted_labels = [labels[id] for id in predicted_ids[0]]
print('Predicted labels:', predicted_labels)
