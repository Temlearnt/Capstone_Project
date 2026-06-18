# backend/app/services/batch_processor.py
import asyncio
import math
from typing import List, Dict, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Batch processor untuk screening CV dalam jumlah besar.
    
    Contoh penggunaan:
        processor = BatchProcessor(batch_size=10)
        results = await processor.process_in_batches(cv_list, process_func, on_progress)
    """
    
    def __init__(self, batch_size: int = 10, max_concurrent: int = 2):
        """
        Args:
            batch_size: Jumlah CV per batch
            max_concurrent: Jumlah batch yang diproses paralel (max 5)
        """
        self.batch_size = batch_size
        self.max_concurrent = min(max_concurrent, 5)
    
    def split_into_batches(self, items: List) -> List[List]:
        """Membagi list menjadi batch-batch kecil"""
        batches = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batches.append(batch)
        return batches
    
    async def process_in_batches(
        self,
        items: List,
        process_func: Callable,
        on_progress: Optional[Callable] = None,
        on_batch_complete: Optional[Callable] = None
    ) -> List:
        """
        Memproses items dalam batch.
        
        Args:
            items: List CV yang akan diproses
            process_func: Fungsi async yang memproses satu batch
            on_progress: Callback untuk update progress (batch_index, total_batches, progress_percent)
            on_batch_complete: Callback setelah batch selesai (batch_index, results)
        
        Returns:
            List hasil dari semua batch
        """
        batches = self.split_into_batches(items)
        total_batches = len(batches)
        all_results = []
        
        logger.info(f"Starting batch processing: {len(items)} items, {total_batches} batches, batch_size={self.batch_size}")
        
        # Process batches with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_batch_with_semaphore(batch_idx: int, batch: List):
            async with semaphore:
                logger.debug(f"Processing batch {batch_idx + 1}/{total_batches}")
                try:
                    batch_results = await process_func(batch)
                except Exception as e:
                    logger.error(f"Batch {batch_idx + 1} failed: {e}")
                    batch_results = []  # atau raise, tergantung kebutuhan
                
                if on_batch_complete:
                    await on_batch_complete(batch_idx, batch_results)
                
                if on_progress:
                    progress = ((batch_idx + 1) / total_batches) * 100
                    await on_progress(batch_idx + 1, total_batches, progress)
                
                return batch_results
        
        # Create tasks for all batches
        tasks = [
            process_batch_with_semaphore(i, batch) 
            for i, batch in enumerate(batches)
        ]
        
        # Wait for all batches to complete
        batch_results = await asyncio.gather(*tasks)
        
        # Flatten results
        for results in batch_results:
            all_results.extend(results)
        
        logger.info(f"Batch processing completed: {len(all_results)} items processed")
        return all_results
    
    def get_batch_info(self, total_items: int) -> dict:
        """Informasi tentang batch processing"""
        num_batches = math.ceil(total_items / self.batch_size)
        return {
            "total_items": total_items,
            "batch_size": self.batch_size,
            "num_batches": num_batches,
            "estimated_chunks": num_batches,
            "max_concurrent": self.max_concurrent
        }

    