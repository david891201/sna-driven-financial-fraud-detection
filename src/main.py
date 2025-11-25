import os
from datetime import datetime
import pandas as pd

from src.sna.pipeline import run_pipeline
from src.utils.utils import load_config, setup_logger
from src.utils.args_parser import parse_args

def main():
    # Parse arguments
    args = parse_args()

    # Setup logging
    app_home = os.environ.get('APP_HOME', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(app_home, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger = setup_logger(log_file)

    # Load configuration
    config = load_config(args.config, args.env)

    logger.info(f"正在執行{os.path.basename(__file__)}")
    logger.info(f"Using config from: {args.config}")
    logger.info(f"Environment: {args.env}")
    logger.info(f"Run date: {args.date}")

    try:
        result_df = run_pipeline(args.date, config)
        result_df.to_csv("result.csv", index=False, encoding='big5')
        logger.info("Job completed successfully")
    except Exception as e:
        logger.error(f"An error occurs:{e}", exc_info=True)
    
if __name__ == "__main__":
    main()