"""
Threshold Optimization and Validation Module for CME Detection
==============================================================

This module provides advanced techniques for:
1. Optimizing detection thresholds based on background statistics
2. Validating CME detection methods
3. Statistical analysis of solar wind parameters
4. ROC analysis and performance metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
from sklearn.metrics import roc_curve, auc, precision_recall_curve
import logging

logger = logging.getLogger(__name__)

class ThresholdOptimizer:
    """
    Advanced threshold optimization for CME detection
    """
    
    def __init__(self, cme_system):
        """
        Initialize with a CME detection system
        
        Args:
            cme_system: Instance of CMEDetectionSystem
        """
        self.cme_system = cme_system
        self.background_stats = {}
        self.optimal_thresholds = {}
        self.validation_results = {}
    
    def calculate_background_statistics(self, window_days=30, chunk_size=100_000):
        """
        Calculate background statistics for each parameter with chunking for large datasets
        
        Args:
            window_days (int): Number of days for rolling background calculation
            chunk_size (int): Number of rows to process in each chunk
        """
        logger.info("Calculating background statistics...")
        
        for instrument, df in self.cme_system.processed_data.items():
            try:
                if len(df) == 0:
                    logger.warning(f"Skipping {instrument}: empty dataset")
                    continue
                
                stats_dict = {}
                df = df.set_index('datetime')
                
                if instrument == 'swepam':
                    params = ['Bulk_Speed', 'Proton_Density', 'Ion_Temperature']
                elif instrument == 'mag':
                    params = ['Bt', 'Bx', 'By', 'Bz']
                elif instrument in ['epam', 'sis']:
                    params = [col for col in df.columns if 'Proton' in col and col not in ['YR', 'MO', 'DA', 'HH', 'MM']][:5]
                else:
                    continue
                
                window_size = pd.Timedelta(days=window_days)
                
                for param in params:
                    if param in df.columns and df[param].notna().sum() > 100:
                        param_data = df[param].replace([9, 99, 999, 9999, -999, -99, -9], np.nan)
                        param_data = param_data.ffill().bfill()
                        
                        # Process in chunks to reduce memory usage
                        chunks = []
                        for start in range(0, len(param_data), chunk_size):
                            chunk = param_data[start:start + chunk_size]
                            chunk_stats = {}
                            chunk_stats[f'{param}_bg_mean'] = chunk.rolling(window=window_size, center=True, min_periods=10).mean()
                            chunk_stats[f'{param}_bg_std'] = chunk.rolling(window=window_size, center=True, min_periods=10).std()
                            chunk_stats[f'{param}_bg_median'] = chunk.rolling(window=window_size, center=True, min_periods=10).median()
                            chunk_stats[f'{param}_bg_p95'] = chunk.rolling(window=window_size, center=True, min_periods=10).quantile(0.95)
                            chunk_stats[f'{param}_bg_p05'] = chunk.rolling(window=window_size, center=True, min_periods=10).quantile(0.05)
                            chunks.append(pd.DataFrame(chunk_stats, index=chunk.index))
                        
                        # Combine chunks
                        chunk_df = pd.concat(chunks)
                        df[f'{param}_bg_mean'] = chunk_df[f'{param}_bg_mean']
                        df[f'{param}_bg_std'] = chunk_df[f'{param}_bg_std']
                        df[f'{param}_bg_median'] = chunk_df[f'{param}_bg_median']
                        df[f'{param}_bg_p95'] = chunk_df[f'{param}_bg_p95']
                        df[f'{param}_bg_p05'] = chunk_df[f'{param}_bg_p05']
                        
                        df[f'{param}_normalized'] = (param_data - df[f'{param}_bg_mean']) / df[f'{param}_bg_std']
                        df[f'{param}_percentile'] = param_data.rolling(window=window_size, center=True, min_periods=10).rank(pct=True)
                        
                        stats_dict[param] = {
                            'mean': param_data.mean(),
                            'std': param_data.std(),
                            'median': param_data.median(),
                            'p95': param_data.quantile(0.95),
                            'p05': param_data.quantile(0.05),
                            'p99': param_data.quantile(0.99),
                            'p01': param_data.quantile(0.01),
                            'missing_count': param_data.isna().sum()
                        }
                
                self.background_stats[instrument] = stats_dict
                self.cme_system.processed_data[instrument] = df.reset_index()
                logger.info(f"Background statistics calculated for {instrument}")
                
            except Exception as e:
                logger.error(f"Error calculating background statistics for {instrument}: {str(e)}")
    
    def optimize_thresholds_statistical(self, sigma_levels=[1.5, 2, 2.5, 3]):
        """
        Optimize thresholds based on statistical significance levels
        
        Args:
            sigma_levels (list): List of sigma levels to test
        """
        logger.info("Optimizing thresholds using statistical methods...")
        
        optimal_thresholds = {}
        
        for instrument, stats_dict in self.background_stats.items():
            instrument_thresholds = {}
            
            for param, stats in stats_dict.items():
                param_thresholds = {}
                missing_ratio = stats['missing_count'] / self.cme_system.processed_data[instrument].shape[0]
                adjustment_factor = 1.0 if missing_ratio < 0.3 else 1.5
                
                for sigma in sigma_levels:
                    adjusted_sigma = sigma * adjustment_factor
                    upper_threshold = stats['mean'] + adjusted_sigma * stats['std']
                    lower_threshold = stats['mean'] - adjusted_sigma * stats['std']
                    percentile_threshold = stats['p95'] if sigma <= 2 else stats['p99']
                    
                    param_thresholds[f'{sigma}sigma_upper'] = upper_threshold
                    param_thresholds[f'{sigma}sigma_lower'] = lower_threshold
                    param_thresholds[f'{sigma}sigma_percentile'] = percentile_threshold
                
                instrument_thresholds[param] = param_thresholds
            
            optimal_thresholds[instrument] = instrument_thresholds
        
        self.optimal_thresholds = optimal_thresholds
        logger.info("Statistical threshold optimization completed")
        
        return optimal_thresholds
    
    def create_synthetic_cme_events(self, num_events=50):
        """
        Create synthetic CME events for validation
        
        Args:
            num_events (int): Number of synthetic events to create
        """
        logger.info(f"Creating {num_events} synthetic CME events for validation...")
        
        synthetic_events = []
        
        for instrument, df in self.cme_system.processed_data.items():
            if len(df) < 100:
                logger.warning(f"Skipping {instrument}: insufficient data ({len(df)} rows)")
                continue
                
            df = df.set_index('datetime')
            instrument_events = []
            stats = self.background_stats.get(instrument, {})
            
            for i in range(num_events):
                valid_indices = df.index[df.index.notna()]
                if len(valid_indices) < 100:
                    continue
                start_time = np.random.choice(valid_indices[50:-50])
                duration_hours = np.random.uniform(2, 24)
                end_time = start_time + pd.Timedelta(hours=duration_hours)
                
                event = {
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_hours': duration_hours,
                    'instrument': instrument,
                    'is_synthetic': True
                }
                
                if instrument == 'swepam':
                    speed_stats = stats.get('Bulk_Speed', {'mean': 400, 'std': 100})
                    density_stats = stats.get('Proton_Density', {'mean': 5, 'std': 2})
                    temp_stats = stats.get('Ion_Temperature', {'mean': 1e5, 'std': 5e4})
                    
                    event['speed_enhancement'] = np.random.uniform(
                        speed_stats['mean'] + speed_stats['std'],
                        speed_stats['mean'] + 3 * speed_stats['std']
                    )
                    event['density_enhancement'] = np.random.uniform(1.5, 5)
                    event['temp_depression'] = np.random.uniform(0.5, 0.8)
                
                elif instrument == 'mag':
                    bt_stats = stats.get('Bt', {'mean': 5, 'std': 2})
                    event['field_rotation'] = np.random.uniform(20, 60)
                    event['field_enhancement'] = np.random.uniform(
                        bt_stats['mean'] + bt_stats['std'],
                        bt_stats['mean'] + 3 * bt_stats['std']
                    )
                
                elif instrument in ['epam', 'sis']:
                    proton_cols = [col for col in df.columns if 'Proton' in col and col not in ['YR', 'MO', 'DA', 'HH', 'MM']]
                    if proton_cols:
                        proton_stats = stats.get(proton_cols[0], {'mean': 1e3, 'std': 1e2})
                        event['particle_enhancement'] = np.random.uniform(
                            proton_stats['mean'] + proton_stats['std'],
                            proton_stats['mean'] + 3 * proton_stats['std']
                        )
                
                instrument_events.append(event)
            
            synthetic_events.extend(instrument_events)
            df = df.reset_index()
        
        self.synthetic_events = pd.DataFrame(synthetic_events)
        logger.info(f"Created {len(self.synthetic_events)} synthetic events")
        
        return self.synthetic_events
    
    def validate_detection_performance(self, threshold_sets=None):
        """
        Validate detection performance using different threshold sets
        
        Args:
            threshold_sets (dict): Dictionary of threshold sets to test
        """
        logger.info("Validating detection performance...")
        
        if threshold_sets is None:
            threshold_sets = {
                '1.5sigma': self._extract_sigma_thresholds(1.5),
                '2sigma': self._extract_sigma_thresholds(2),
                '2.5sigma': self._extract_sigma_thresholds(2.5),
                '3sigma': self._extract_sigma_thresholds(3)
            }
        
        validation_results = {}
        
        for threshold_name, thresholds in threshold_sets.items():
            logger.info(f"Testing threshold set: {threshold_name}")
            detections = self._apply_thresholds_and_detect(thresholds)
            
            if hasattr(self, 'synthetic_events') and not self.synthetic_events.empty:
                metrics = self._calculate_validation_metrics(detections, self.synthetic_events)
                validation_results[threshold_name] = metrics
            else:
                validation_results[threshold_name] = {
                    'true_positives': 0,
                    'false_positives': 0,
                    'false_negatives': 0,
                    'precision': 0.0,
                    'recall': 0.0,
                    'f1_score': 0.0
                }
        
        self.validation_results = validation_results
        return validation_results
    
    def _extract_sigma_thresholds(self, sigma_level):
        """Extract thresholds for a specific sigma level"""
        sigma_thresholds = {}
        
        for instrument, instrument_thresholds in self.optimal_thresholds.items():
            sigma_thresholds[instrument] = {}
            for param, param_thresholds in instrument_thresholds.items():
                sigma_key = f'{sigma_level}sigma_upper'
                if sigma_key in param_thresholds:
                    sigma_thresholds[instrument][param] = param_thresholds[sigma_key]
        
        return sigma_thresholds
    
    def _apply_thresholds_and_detect(self, thresholds):
        """Apply thresholds and perform detection"""
        detections = []
        
        for instrument, df in self.cme_system.processed_data.items():
            if len(df) == 0 or instrument not in thresholds:
                continue
            
            df = df.set_index('datetime')
            instrument_thresholds = thresholds[instrument]
            detection_flags = pd.Series(False, index=df.index)
            
            for param, threshold in instrument_thresholds.items():
                if param in df.columns:
                    if 'speed' in param.lower() or 'density' in param.lower() or 'proton' in param.lower():
                        detection_flags |= (df[param] > threshold)
                    elif 'temp' in param.lower():
                        detection_flags |= (df[param] < threshold)
            
            detected_times = df[detection_flags].index
            for det_time in detected_times:
                detections.append({
                    'detection_time': det_time,
                    'instrument': instrument
                })
            
            df = df.reset_index()
        
        return pd.DataFrame(detections)
    
    def _calculate_validation_metrics(self, detections, synthetic_events, tolerance_hours=2):
        """Calculate validation metrics"""
        tolerance = timedelta(hours=tolerance_hours)
        
        true_positives = 0
        false_negatives = 0
        false_positives = 0
        
        detection_times = {(row['detection_time'], row['instrument']) for _, row in detections.iterrows()}
        synthetic_times = {(row['start_time'], row['instrument']) for _, row in synthetic_events.iterrows()}
        
        for synth_time, instrument in synthetic_times:
            matched = False
            for det_time, det_instrument in detection_times:
                if det_instrument == instrument and abs(det_time - synth_time) <= tolerance:
                    true_positives += 1
                    matched = True
                    break
            if not matched:
                false_negatives += 1
        
        for det_time, instrument in detection_times:
            matched = False
            for synth_time, synth_instrument in synthetic_times:
                if synth_instrument == instrument and abs(det_time - synth_time) <= tolerance:
                    matched = True
                    break
            if not matched:
                false_positives += 1
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }
    
    def plot_threshold_analysis(self, figsize=(15, 10)):
        """Plot threshold analysis results"""
        logger.info("Creating threshold analysis plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.ravel()
        
        self._plot_parameter_distributions(axes[0])
        self._plot_performance_vs_thresholds(axes[1])
        self._plot_roc_analysis(axes[2])
        self._plot_validation_metrics(axes[3])
        
        plt.tight_layout()
        plt.savefig('threshold_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info("Threshold analysis plots saved as 'threshold_analysis.png'")
    
    def _plot_parameter_distributions(self, ax):
        """Plot parameter distributions with threshold lines"""
        if 'swepam' in self.cme_system.processed_data:
            df = self.cme_system.processed_data['swepam'].set_index('datetime')
            if 'Bulk_Speed' in df.columns:
                ax.hist(df['Bulk_Speed'].dropna(), bins=50, alpha=0.7, density=True, label='Bulk Speed')
                
                if 'swepam' in self.optimal_thresholds and 'Bulk_Speed' in self.optimal_thresholds['swepam']:
                    thresholds = self.optimal_thresholds['swepam']['Bulk_Speed']
                    for sigma in [1.5, 2, 2.5, 3]:
                        key = f'{sigma}sigma_upper'
                        if key in thresholds:
                            ax.axvline(thresholds[key], color='red', linestyle='--', 
                                     alpha=0.7, label=f'{sigma}σ threshold')
                
                ax.set_xlabel('Solar Wind Speed (km/s)')
                ax.set_ylabel('Density')
                ax.set_title('Bulk Speed Distribution with Thresholds')
                ax.legend()
                ax.grid(True, alpha=0.3)
    
    def _plot_performance_vs_thresholds(self, ax):
        """Plot performance metrics vs threshold levels"""
        if self.validation_results:
            threshold_names = list(self.validation_results.keys())
            precisions = [self.validation_results[name]['precision'] for name in threshold_names]
            recalls = [self.validation_results[name]['recall'] for name in threshold_names]
            f1_scores = [self.validation_results[name]['f1_score'] for name in threshold_names]
            
            x = np.arange(len(threshold_names))
            width = 0.25
            
            ax.bar(x - width, precisions, width, label='Precision', alpha=0.8)
            ax.bar(x, recalls, width, label='Recall', alpha=0.8)
            ax.bar(x + width, f1_scores, width, label='F1-Score', alpha=0.8)
            
            ax.set_xlabel('Threshold Sets')
            ax.set_ylabel('Performance Metrics')
            ax.set_title('Performance vs Threshold Levels')
            ax.set_xticks(x)
            ax.set_xticklabels(threshold_names, rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 1)
    
    def _plot_roc_analysis(self, ax):
        """Plot ROC curve analysis"""
        if hasattr(self, 'synthetic_events') and not self.synthetic_events.empty:
            for threshold_name, metrics in self.validation_results.items():
                fpr = metrics['false_positives'] / (metrics['false_positives'] + metrics['true_positives'] + 1e-10)
                tpr = metrics['recall']
                ax.plot(fpr, tpr, 'o-', label=f'{threshold_name} (F1={metrics["f1_score"]:.2f})')
            
            ax.plot([0, 1], [0, 1], 'k--', alpha=0.5)
            ax.set_xlabel('False Positive Rate')
            ax.set_ylabel('True Positive Rate')
            ax.set_title('ROC Analysis')
            ax.legend()
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'ROC analysis requires synthetic events', 
                    ha='center', va='center', fontsize=10, alpha=0.7)
            ax.set_xlabel('False Positive Rate')
            ax.set_ylabel('True Positive Rate')
            ax.set_title('ROC Analysis')
            ax.grid(True, alpha=0.3)
    
    def _plot_validation_metrics(self, ax):
        """Plot validation metrics comparison"""
        if self.validation_results:
            metrics = ['precision', 'recall', 'f1_score']
            threshold_names = list(self.validation_results.keys())
            
            metric_data = []
            for metric in metrics:
                values = [self.validation_results[name][metric] for name in threshold_names]
                metric_data.append(values)
            
            x = np.arange(len(threshold_names))
            colors = ['blue', 'orange', 'green']
            
            for i, (metric, values) in enumerate(zip(metrics, metric_data)):
                ax.plot(x, values, 'o-', color=colors[i], label=metric.capitalize(), linewidth=2)
            
            ax.set_xlabel('Threshold Sets')
            ax.set_ylabel('Metric Value')
            ax.set_title('Validation Metrics Comparison')
            ax.set_xticks(x)
            ax.set_xticklabels(threshold_names, rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 1)
    
    def generate_threshold_report(self):
        """Generate comprehensive threshold optimization report"""
        logger.info("Generating threshold optimization report...")
        
        report = []
        report.append("=" * 80)
        report.append("THRESHOLD OPTIMIZATION AND VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("BACKGROUND STATISTICS SUMMARY:")
        report.append("-" * 50)
        for instrument, stats_dict in self.background_stats.items():
            report.append(f"\n{instrument.upper()}:")
            for param, stats in stats_dict.items():
                report.append(f"  {param}:")
                report.append(f"    Mean: {stats['mean']:.2f}")
                report.append(f"    Std:  {stats['std']:.2f}")
                report.append(f"    95th percentile: {stats['p95']:.2f}")
                report.append(f"    Missing values: {stats['missing_count']}")
        
        report.append("\n\nOPTIMAL THRESHOLDS:")
        report.append("-" * 50)
        for instrument, instrument_thresholds in self.optimal_thresholds.items():
            report.append(f"\n{instrument.upper()}:")
            for param, param_thresholds in instrument_thresholds.items():
                report.append(f"  {param}:")
                for threshold_type, value in param_thresholds.items():
                    if 'upper' in threshold_type:
                        report.append(f"    {threshold_type}: {value:.2f}")
        
        report.append("\n\nVALIDATION RESULTS:")
        report.append("-" * 50)
        for threshold_name, metrics in self.validation_results.items():
            report.append(f"\n{threshold_name}:")
            report.append(f"  Precision: {metrics['precision']:.3f}")
            report.append(f"  Recall:    {metrics['recall']:.3f}")
            report.append(f"  F1-Score:  {metrics['f1_score']:.3f}")
            report.append(f"  True Positives:  {metrics['true_positives']}")
            report.append(f"  False Positives: {metrics['false_positives']}")
            report.append(f"  False Negatives: {metrics['false_negatives']}")
        
        report.append("\n\nRECOMMENDATIONS:")
        report.append("-" * 50)
        if self.validation_results:
            best_threshold = max(self.validation_results.keys(), 
                               key=lambda x: self.validation_results[x]['f1_score'])
            report.append(f"Best performing threshold set: {best_threshold}")
            report.append(f"F1-Score: {self.validation_results[best_threshold]['f1_score']:.3f}")
        
        report.append("\nFor CME detection in operational mode:")
        report.append("1. Use 1.5-sigma thresholds for high sensitivity")
        report.append("2. Use 2-sigma thresholds for balanced performance")
        report.append("3. Use 3-sigma thresholds for high specificity")
        report.append("4. Monitor missing data and HHMM alignment issues")
        
        report.append("\n" + "=" * 80)
        
        report_text = "\n".join(report)
        with open('threshold_optimization_report.txt', 'w') as f:
            f.write(report_text)
        
        print(report_text)
        logger.info("Threshold optimization report saved")
        
        return report_text

def run_threshold_analysis(cme_system):
    """
    Run complete threshold optimization analysis
    
    Args:
        cme_system: Instance of CMEDetectionSystem
    """
    logger.info("Starting threshold optimization analysis...")
    
    optimizer = ThresholdOptimizer(cme_system)
    optimizer.calculate_background_statistics()
    optimizer.optimize_thresholds_statistical()
    optimizer.create_synthetic_cme_events()
    optimizer.validate_detection_performance()
    optimizer.plot_threshold_analysis()
    optimizer.generate_threshold_report()
    
    logger.info("Threshold optimization analysis completed!")
    return optimizer

if __name__ == "__main__":
    from cme_detection_system import CMEDetectionSystem
    
    cme_system = CMEDetectionSystem("csv_file")
    cme_system.load_data()
    cme_system.preprocess_data()
    cme_system.derive_features()
    
    optimizer = run_threshold_analysis(cme_system)