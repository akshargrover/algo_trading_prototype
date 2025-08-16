import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from data_fetcher import DataFetcher
from strategy import apply_indicators, generate_signals
from backtester import Backtester
from ml_model import MLPredictor
from csv_logger import CSVSLogger
from utils import setup_logger
import pandas as pd

# Load environment variables
load_dotenv()

# Configuration
TICKERS = os.getenv("TICKERS", "RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS,ICICIBANK.NS").split(",")
SYMBOL = os.getenv("SYMBOL", "RELIANCE.NS")
INTERVAL = os.getenv("INTERVAL", "1d")
PERIOD = os.getenv("PERIOD", "2y")
RSI_PERIOD = int(os.getenv("RSI_PERIOD", 14))
SMA_SHORT = int(os.getenv("SMA_SHORT", 20))
SMA_LONG = int(os.getenv("SMA_LONG", 50))
TRADE_QTY = int(os.getenv("TRADE_QTY", 100))
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", 100000))
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", 2.0))

def run_single_stock_analysis(symbol: str, period: str = "1y", interval: str = "1d"):
    """Run complete analysis for a single stock"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting analysis for {symbol}")
        
        # 1. Data Fetching
        logger.info("Step 1: Fetching stock data...")
        fetcher = DataFetcher(delay_between_requests=1.0)
        df = fetcher.fetch_stock_data(symbol, period, interval)
        
        # Validate data quality
        quality_report = fetcher.validate_data_quality(df)
        logger.info(f"Data quality score: {quality_report['quality_score']}")
        
        if quality_report['quality_score'] < 70:
            logger.warning(f"Low data quality for {symbol}: {quality_report['issues']}")
        
        # 2. Apply Technical Indicators
        logger.info("Step 2: Applying technical indicators...")
        df = apply_indicators(df, RSI_PERIOD, SMA_SHORT, SMA_LONG)
        
        # 3. Generate Trading Signals
        logger.info("Step 3: Generating trading signals...")
        df = generate_signals(df)
        
        # 4. Run Backtest
        logger.info("Step 4: Running backtest...")
        backtester = Backtester(INITIAL_CAPITAL, RISK_PER_TRADE)
        trades_df = backtester.backtest(df, symbol)
        performance_metrics = backtester.get_performance_metrics()
        
        # 5. Train ML Model
        logger.info("Step 5: Training ML model...")
        ml_predictor = MLPredictor()
        df_features = ml_predictor.engineer_features(df)
        logger.info(f"Feature engineering completed: {len(df_features)} rows, {len(df_features.columns)} columns")
        
        X, y, feature_cols = ml_predictor.prepare_features(df_features)
        logger.info(f"Feature preparation completed: X shape {X.shape if not X.empty else 'empty'}, y shape {y.shape if not y.empty else 'empty'}")
        
        # Check minimum data requirements for ML training
        min_samples = 100  # Minimum samples needed for reliable ML training
        if not X.empty and not y.empty and len(X) >= min_samples:
            logger.info(f"Sufficient data for ML training: {len(X)} samples, {len(feature_cols)} features")
            ml_results = ml_predictor.train_models(X, y)
            feature_importance = ml_predictor.get_feature_importance()
        else:
            if X.empty or y.empty:
                logger.warning(f"Insufficient data for ML training: X has {len(X) if not X.empty else 0} samples, y has {len(y) if not y.empty else 0} samples")
            else:
                logger.warning(f"Insufficient data for ML training: Only {len(X)} samples available, need at least {min_samples}")
            ml_results = {}
            feature_importance = pd.DataFrame()
        
        # 6. Log Results to CSV Files
        logger.info("Step 6: Logging results to CSV files...")
        try:
            csv_logger = CSVSLogger()
            
            # Log trades
            if not trades_df.empty:
                csv_logger.log_trades(trades_df, f"{symbol}_Trades")
            
            # Log performance metrics
            csv_logger.log_performance_metrics(performance_metrics, f"{symbol}_Performance")
            
            # Log ML results
            if ml_results:
                csv_logger.log_ml_results(ml_results, f"{symbol}_ML_Results")
            
            # Log feature importance
            if not feature_importance.empty:
                csv_logger.log_feature_importance(feature_importance, f"{symbol}_Feature_Importance")
            
            # Log equity curve
            if backtester.equity_curve:
                csv_logger.log_equity_curve(backtester.equity_curve, f"{symbol}_Equity_Curve")
            
            logger.info("Successfully logged all results to CSV files")
            
        except Exception as e:
            logger.error(f"Failed to log to CSV files: {e}")
        
        # 7. Print Summary
        logger.info("=" * 50)
        logger.info(f"ANALYSIS SUMMARY FOR {symbol}")
        logger.info("=" * 50)
        
        if not trades_df.empty:
            logger.info(f"Total Trades: {performance_metrics.get('Total_Trades', 0)}")
            logger.info(f"Win Rate: {performance_metrics.get('Win_Rate', 0):.2f}%")
            logger.info(f"Total P&L: ${performance_metrics.get('Total_PnL', 0):.2f}")
            logger.info(f"Total Return: {performance_metrics.get('Total_Return_Pct', 0):.2f}%")
            logger.info(f"Max Drawdown: {performance_metrics.get('Max_Drawdown_Pct', 0):.2f}%")
            logger.info(f"Sharpe Ratio: {performance_metrics.get('Sharpe_Ratio', 0):.4f}")
        
        if ml_results:
            best_model = max(ml_results.keys(), key=lambda x: ml_results[x]['cv_mean'])
            best_accuracy = ml_results[best_model]['accuracy']
            best_cv = ml_results[best_model]['cv_mean']
            logger.info(f"Best ML Model: {best_model}")
            logger.info(f"Test Accuracy: {best_accuracy:.4f}")
            logger.info(f"Cross-validation: {best_cv:.4f}")
        
        return {
            'symbol': symbol,
            'trades': trades_df,
            'performance': performance_metrics,
            'ml_results': ml_results,
            'feature_importance': feature_importance
        }
        
    except Exception as e:
        logger.error(f"Analysis failed for {symbol}: {e}")
        return None

def run_portfolio_analysis(tickers: list, period: str = "1y", interval: str = "1d"):
    """Run analysis for multiple stocks and generate portfolio summary"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting portfolio analysis for {len(tickers)} stocks")
    
    results = {}
    successful_analyses = 0
    
    for ticker in tickers:
        try:
            result = run_single_stock_analysis(ticker, period, interval)
            if result:
                results[ticker] = result
                successful_analyses += 1
        except Exception as e:
            logger.error(f"Failed to analyze {ticker}: {e}")
    
    # Generate portfolio summary
    if results:
        portfolio_summary = generate_portfolio_summary(results)
        
        # Log portfolio summary to CSV
        try:
            csv_logger = CSVSLogger()
            csv_logger.log_summary_report(portfolio_summary, "Portfolio_Summary")
            logger.info("Portfolio summary logged to CSV")
        except Exception as e:
            logger.error(f"Failed to log portfolio summary: {e}")
        
        return results, portfolio_summary
    
    return results, {}

def generate_portfolio_summary(results: dict) -> dict:
    """Generate comprehensive portfolio summary"""
    summary = {
        'Portfolio_Overview': {
            'Total_Stocks': len(results),
            'Analysis_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        'Performance_Summary': {},
        'ML_Summary': {},
        'Risk_Metrics': {}
    }
    
    # Aggregate performance metrics
    total_pnl = 0
    total_trades = 0
    total_return = 0
    max_drawdowns = []
    sharpe_ratios = []
    
    for ticker, result in results.items():
        if 'performance' in result:
            perf = result['performance']
            total_pnl += perf.get('Total_PnL', 0)
            total_trades += perf.get('Total_Trades', 0)
            total_return += perf.get('Total_Return_Pct', 0)
            
            if 'Max_Drawdown_Pct' in perf:
                max_drawdowns.append(perf['Max_Drawdown_Pct'])
            
            if 'Sharpe_Ratio' in perf:
                sharpe_ratios.append(perf['Sharpe_Ratio'])
    
    if results:
        summary['Performance_Summary'] = {
            'Total_PnL': total_pnl,
            'Total_Trades': total_trades,
            'Average_Return_Pct': total_return / len(results),
            'Average_Max_Drawdown': sum(max_drawdowns) / len(max_drawdowns) if max_drawdowns else 0,
            'Average_Sharpe_Ratio': sum(sharpe_ratios) / len(sharpe_ratios) if sharpe_ratios else 0
        }
    
    # Aggregate ML metrics
    ml_accuracies = []
    for ticker, result in results.items():
        if 'ml_results' in result and result['ml_results']:
            for model_name, model_result in result['ml_results'].items():
                if 'accuracy' in model_result:
                    ml_accuracies.append(model_result['accuracy'])
    
    if ml_accuracies:
        summary['ML_Summary'] = {
            'Average_ML_Accuracy': sum(ml_accuracies) / len(ml_accuracies),
            'Best_ML_Accuracy': max(ml_accuracies),
            'Worst_ML_Accuracy': min(ml_accuracies)
        }
    
    return summary

def main():
    """Main execution function"""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Algo Trading Prototype Analysis")
    logger.info("=" * 50)
    logger.info(f"Configured stocks: {', '.join(TICKERS)}")
    logger.info(f"Data period: {PERIOD}")
    logger.info(f"Data interval: {INTERVAL}")
    logger.info("=" * 50)
    
    try:
        # Check if running single stock or portfolio analysis
        if len(sys.argv) > 1 and sys.argv[1] == "--single":
            # Single stock analysis
            logger.info("Running single stock analysis...")
            result = run_single_stock_analysis(SYMBOL, PERIOD, INTERVAL)
            
            if result:
                logger.info("Single stock analysis completed successfully!")
            else:
                logger.error("Single stock analysis failed!")
                
        elif len(sys.argv) > 1 and sys.argv[1] == "--portfolio":
            # Portfolio analysis
            logger.info("Running portfolio analysis...")
            results, summary = run_portfolio_analysis(TICKERS, PERIOD, INTERVAL)
            
            logger.info("Portfolio analysis completed!")
            logger.info(f"Successfully analyzed {len(results)} stocks")
            
        else:
            # Default behavior: Run portfolio analysis if multiple stocks, single stock if only one
            if len(TICKERS) > 1:
                logger.info(f"Multiple stocks detected ({len(TICKERS)}), running portfolio analysis...")
                results, summary = run_portfolio_analysis(TICKERS, PERIOD, INTERVAL)
                
                logger.info("Portfolio analysis completed!")
                logger.info(f"Successfully analyzed {len(results)} stocks")
            else:
                logger.info("Single stock detected, running single stock analysis...")
                result = run_single_stock_analysis(SYMBOL, PERIOD, INTERVAL)
                
                if result:
                    logger.info("Single stock analysis completed successfully!")
                else:
                    logger.error("Single stock analysis failed!")
        
        logger.info("=" * 50)
        logger.info("Analysis completed!")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
