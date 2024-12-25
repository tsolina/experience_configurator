# services/logging_service.py
import inspect

class LoggingService:
    @staticmethod
    def log_point(instance, message="", **variables):
        """Logs debug information for a specific checkpoint."""
        cls_name = instance.__class__.__name__
        frame = inspect.currentframe().f_back
        func_name = frame.f_code.co_name
        log_message = f"{cls_name}.{func_name}.{message}" if message else f"{cls_name}.{func_name}"
        
        if variables:
            log_message += f" | Variables: {variables}"
        
        print(log_message)
