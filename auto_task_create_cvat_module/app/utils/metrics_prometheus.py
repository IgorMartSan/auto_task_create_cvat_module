import logging
from prometheus_client import Summary, Counter, Gauge

FRAME_LOSS_COUNTER = Counter('frame_loss_total', 'Total number of lost frames')
LOG_MESSAGES_SUMMARY = Summary('log_messages_summary', 'Summary of log messages')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
LOOP_EXECUTION_TIME_GAUGE = Gauge('loop_execution_time_seconds', 'Time taken for each loop iteration')
LARGEST_MEASUREMENT_WIDTH_GAUGE =  Gauge('largest_measurement_width', 'largest measurement width')

def detect_and_log_frame_loss_couter(frame_id_current, frame_id_ant=None):    
    if frame_id_ant is not None and frame_id_current != frame_id_ant + 1:
        lost_frames = frame_id_current - frame_id_ant - 1
        # Using ic for debugging
        #ic(frame_id_ant, frame_id_current, lost_frames)
        
        # Replacing direct print statement with ic for a more descriptive debug message
        logger_error_msg = (f"A image was lost ( Previous frame id: {frame_id_ant}; " +
                            f"Current frame id: {frame_id_current}; " +
                            f"Number images lost: {lost_frames})")
        logging.warning(logger_error_msg)
        #logger.error(logger_error_msg)
        #ic(logger_error_msg)

        # Increment the counter by the number of frames lost
        FRAME_LOSS_COUNTER.inc(lost_frames)

        frame_id_ant = frame_id_current

        return  frame_id_ant
    
def register_log_message_summary(message):
        LOG_MESSAGES_SUMMARY.observe(len(message))

def register_execution_time_gauge(execution_time):
        LOOP_EXECUTION_TIME_GAUGE.set(execution_time)

def register_width_calculator(execution_time):
        LOOP_EXECUTION_TIME_GAUGE.set(execution_time)

def largest_measurement_width(width):
        LARGEST_MEASUREMENT_WIDTH_GAUGE.set(width)


