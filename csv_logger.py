import pandas as pd
import os
import csv
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVSLogger:
    """CSV logger for algo trading results"""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"CSV Logger initialized. Output directory: {output_dir}")
    
    def log_trades(self, trades_df: pd.DataFrame, filename: str = "trades"):
        """Log comprehensive trade data to CSV"""
        if trades_df.empty:
            logger.warning("No trades to log")
            return
        
        try:
            filepath = os.path.join(self.output_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            trades_df.to_csv(filepath, index=False)
            logger.info(f"Successfully logged {len(trades_df)} trades to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to log trades to CSV: {e}")
            raise
    
    def log_performance_metrics(self, metrics: Dict, filename: str = "performance"):
        """Log performance metrics to CSV"""
        try:
            filepath = os.path.join(self.output_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            # Convert metrics to DataFrame
            metrics_df = pd.DataFrame([
                ["Metric", "Value"],
                ["Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ] + [[metric, str(value)] for metric, value in metrics.items()])
            
            metrics_df.to_csv(filepath, index=False, header=False)
            logger.info(f"Successfully logged performance metrics to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to log performance metrics to CSV: {e}")
            raise
    
    def log_ml_results(self, ml_results: Dict, filename: str = "ml_results"):
        """Log ML model results to CSV"""
        try:
            filepath = os.path.join(self.output_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            # Prepare data
            data = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for model_name, result in ml_results.items():
                if isinstance(result, dict) and 'accuracy' in result:
                    row = {
                        'Model': model_name,
                        'Accuracy': f"{result.get('accuracy', 'N/A'):.4f}",
                        'AUC': f"{result.get('auc', 'N/A'):.4f}" if result.get('auc') else 'N/A',
                        'CV_Mean': f"{result.get('cv_mean', 'N/A'):.4f}",
                        'CV_Std': f"{result.get('cv_std', 'N/A'):.4f}",
                        'Timestamp': timestamp
                    }
                    data.append(row)
            
            if data:
                results_df = pd.DataFrame(data)
                results_df.to_csv(filepath, index=False)
                logger.info(f"Successfully logged ML results to {filepath}")
            else:
                logger.warning("No ML results to log")
            
        except Exception as e:
            logger.error(f"Failed to log ML results to CSV: {e}")
            raise
    
    def log_feature_importance(self, feature_importance_df: pd.DataFrame, filename: str = "feature_importance"):
        """Log feature importance from ML model to CSV"""
        if feature_importance_df.empty:
            logger.warning("No feature importance data to log")
            return
        
        try:
            filepath = os.path.join(self.output_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            # Add timestamp column
            feature_importance_df['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            feature_importance_df.to_csv(filepath, index=False)
            
            logger.info(f"Successfully logged feature importance to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to log feature importance to CSV: {e}")
            raise
    
    def log_equity_curve(self, equity_curve: List[Dict], filename: str = "equity_curve"):
        """Log equity curve data to CSV"""
        if not equity_curve:
            logger.warning("No equity curve data to log")
            return
        
        try:
            filepath = os.path.join(self.output_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            # Convert to DataFrame
            equity_df = pd.DataFrame(equity_curve)
            equity_df['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            equity_df.to_csv(filepath, index=False)
            
            logger.info(f"Successfully logged equity curve to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to log equity curve to CSV: {e}")
            raise
    
    def log_summary_report(self, summary_data: Dict, filename: str = "summary_report"):
        """Log comprehensive summary report to CSV"""
        try:
            filepath = os.path.join(self.output_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            # Prepare data
            data = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for category, metrics in summary_data.items():
                if isinstance(metrics, dict):
                    for metric, value in metrics.items():
                        data.append({
                            'Category': category,
                            'Metric': metric,
                            'Value': str(value),
                            'Timestamp': timestamp
                        })
                else:
                    data.append({
                        'Category': category,
                        'Metric': 'Value',
                        'Value': str(metrics),
                        'Timestamp': timestamp
                    })
            
            if data:
                summary_df = pd.DataFrame(data)
                summary_df.to_csv(filepath, index=False)
                logger.info(f"Successfully logged summary report to {filepath}")
            else:
                logger.warning("No summary data to log")
            
        except Exception as e:
            logger.error(f"Failed to log summary report to CSV: {e}")
            raise

# Legacy functions for backward compatibility
def log_trade(symbol, action, price, qty, file_path="results/trades.csv"):
    """Legacy function for logging individual trades to CSV"""
    # Make sure the folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header if file is new
        if not file_exists:
            writer.writerow(["Timestamp", "Symbol", "Action", "Price", "Quantity"])

        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, action, price, qty])

def log_trades_to_csv(trades, filename):
    """Legacy function for backward compatibility"""
    logger = CSVSLogger()
    if isinstance(trades, pd.DataFrame):
        logger.log_trades(trades, filename)
    else:
        logger.log_trades(pd.DataFrame(trades), filename)

# Example usage
if __name__ == "__main__":
    try:
        # Test the CSV logger
        logger = CSVSLogger()
        
        # Test logging sample data
        sample_trades = pd.DataFrame({
            'Ticker': ['AAPL', 'GOOGL'],
            'Entry_Price': [150.0, 2800.0],
            'Exit_Price': [155.0, 2850.0],
            'PnL': [5.0, 50.0]
        })
        
        logger.log_trades(sample_trades, "Test_Trades")
        
        # Test logging performance metrics
        sample_metrics = {
            'Total_Trades': 10,
            'Win_Rate': 60.0,
            'Total_PnL': 500.0
        }
        
        logger.log_performance_metrics(sample_metrics, "Test_Performance")
        
        print("Test logging completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
