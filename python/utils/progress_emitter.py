import json
import sys


class ProgressEmitter:
    """Emit progress updates to Node.js via stdout"""

    _last_progress = -1
    _last_step = None
    _last_emit_time = 0

    @staticmethod
    def emit(job_id, step, progress, message):
        """
        Emit progress update with throttling to avoid overwhelming the database.
        
        Args:
            job_id (str): Conversion job ID
            step (str): Current step name
            progress (int): Progress percentage (0-100)
            message (str): Status message
        """
        import time
        current_time = time.time()
        
        # Throttling logic:
        # 1. Always emit if the step has changed
        # 2. Always emit if it's the 100% completion
        # 3. Otherwise, only emit if at least 500ms has passed since last update
        #    AND the progress has actually changed.
        time_elapsed = current_time - ProgressEmitter._last_emit_time
        
        if (step != ProgressEmitter._last_step or 
            progress >= 100 or 
            (time_elapsed > 0.5 and progress != ProgressEmitter._last_progress)):
            
            output = {
                'type': 'progress',
                'jobId': job_id,
                'step': step,
                'progress': progress,
                'message': message
            }
            print(json.dumps(output), flush=True)
            
            # Update state
            ProgressEmitter._last_progress = progress
            ProgressEmitter._last_step = step
            ProgressEmitter._last_emit_time = current_time

    @staticmethod
    def emit_result(data):
        """
        Emit final result

        Args:
            data (dict): Result data
        """
        output = {
            'type': 'result',
            'data': data
        }
        print(json.dumps(output), flush=True)

    @staticmethod
    def emit_error(job_id, error_message):
        """
        Emit error

        Args:
            job_id (str): Conversion job ID
            error_message (str): Error message
        """
        output = {
            'type': 'error',
            'jobId': job_id,
            'error': error_message
        }
        print(json.dumps(output), flush=True)

    @staticmethod
    def emit_custom(job_id, type_name, data):
        """
        Emit custom message

        Args:
            job_id (str): Conversion job ID
            type_name (str): Message type
            data (any): Data payload
        """
        output = {
            'type': type_name,
            'jobId': job_id,
            'data': data
        }
        print(json.dumps(output), flush=True)


__all__ = ['ProgressEmitter']
