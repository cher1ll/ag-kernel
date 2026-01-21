#!/usr/bin/env python3
"""
Performance benchmark: Optimized vs Original data processing.

Compares loading and processing performance between different approaches.
"""
import sys
import time
import numpy as np
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from ag_backtester.data import (
    AggTradesFeed, 
    aggregate_ticks, 
    load_data_optimized,
    aggregate_ticks_vectorized
)


def benchmark_data_loading(data_path: str, tick_size: float = 10.0):
    """Benchmark different data loading approaches."""
    
    print("🏁 Data Loading Benchmark")
    print("=" * 50)
    
    results = {}
    
    # 1. Original CSV approach
    print("\n1️⃣ Original CSV Loading (chunked)")
    start_time = time.time()
    
    feed = AggTradesFeed(data_path, tick_size=tick_size, auto_convert=False, force_csv=True)
    trades = feed.load()
    
    original_time = time.time() - start_time
    original_count = len(trades)
    
    print(f"   Time: {original_time:.3f}s")
    print(f"   Ticks: {original_count:,}")
    print(f"   Throughput: {original_count/original_time:,.0f} ticks/s")
    
    results['original_csv'] = {
        'time': original_time,
        'count': original_count,
        'throughput': original_count / original_time
    }
    
    # 2. Optimized batch loading
    print("\n2️⃣ Optimized Batch Loading (Parquet)")
    start_time = time.time()
    
    data, metrics = load_data_optimized(
        data_path=data_path,
        tick_size=tick_size,
        auto_convert=True,
        verbose=False
    )
    
    optimized_time = time.time() - start_time
    optimized_count = len(data['timestamp'])
    
    print(f"   Time: {optimized_time:.3f}s")
    print(f"   Ticks: {optimized_count:,}")
    print(f"   Throughput: {optimized_count/optimized_time:,.0f} ticks/s")
    print(f"   Speedup: {original_time/optimized_time:.1f}x")
    
    results['optimized_batch'] = {
        'time': optimized_time,
        'count': optimized_count,
        'throughput': optimized_count / optimized_time,
        'speedup': original_time / optimized_time
    }
    
    return results


def benchmark_aggregation(data_path: str, tick_size: float = 10.0, bucket_ms: int = 50):
    """Benchmark tick aggregation approaches."""
    
    print("\n\n🔄 Tick Aggregation Benchmark")
    print("=" * 50)
    
    # Load data for aggregation tests
    feed = AggTradesFeed(data_path, tick_size=tick_size, auto_convert=False, force_csv=True)
    trades = feed.load()
    
    # Also load as batch data
    batch_data, _ = load_data_optimized(data_path, tick_size=tick_size, verbose=False)
    
    results = {}
    
    # 1. Original aggregation (iterator-based)
    print(f"\n1️⃣ Original Aggregation (iterator)")
    start_time = time.time()
    
    agg_ticks_original = aggregate_ticks(iter(trades), bucket_ms=bucket_ms, tick_size=tick_size)
    
    original_agg_time = time.time() - start_time
    original_agg_count = len(agg_ticks_original)
    
    print(f"   Time: {original_agg_time:.3f}s")
    print(f"   Input ticks: {len(trades):,}")
    print(f"   Output ticks: {original_agg_count:,}")
    print(f"   Throughput: {len(trades)/original_agg_time:,.0f} ticks/s")
    
    results['original_aggregation'] = {
        'time': original_agg_time,
        'input_count': len(trades),
        'output_count': original_agg_count,
        'throughput': len(trades) / original_agg_time
    }
    
    # 2. Vectorized aggregation
    print(f"\n2️⃣ Vectorized Aggregation (numpy)")
    start_time = time.time()
    
    agg_data_vectorized = aggregate_ticks_vectorized(batch_data, bucket_ms=bucket_ms, tick_size=tick_size)
    
    vectorized_agg_time = time.time() - start_time
    vectorized_agg_count = len(agg_data_vectorized['timestamp'])
    
    print(f"   Time: {vectorized_agg_time:.3f}s")
    print(f"   Input ticks: {len(batch_data['timestamp']):,}")
    print(f"   Output ticks: {vectorized_agg_count:,}")
    print(f"   Throughput: {len(batch_data['timestamp'])/vectorized_agg_time:,.0f} ticks/s")
    print(f"   Speedup: {original_agg_time/vectorized_agg_time:.1f}x")
    
    results['vectorized_aggregation'] = {
        'time': vectorized_agg_time,
        'input_count': len(batch_data['timestamp']),
        'output_count': vectorized_agg_count,
        'throughput': len(batch_data['timestamp']) / vectorized_agg_time,
        'speedup': original_agg_time / vectorized_agg_time
    }
    
    return results


def print_summary(loading_results, aggregation_results):
    """Print benchmark summary."""
    
    print("\n\n📊 BENCHMARK SUMMARY")
    print("=" * 50)
    
    print("\n🚀 Loading Performance:")
    orig_loading = loading_results['original_csv']
    opt_loading = loading_results['optimized_batch']
    
    print(f"  Original CSV:     {orig_loading['throughput']:>10,.0f} ticks/s")
    print(f"  Optimized Batch:  {opt_loading['throughput']:>10,.0f} ticks/s")
    print(f"  Loading Speedup:  {opt_loading['speedup']:>10.1f}x")
    
    print("\n⚡ Aggregation Performance:")
    orig_agg = aggregation_results['original_aggregation']
    vec_agg = aggregation_results['vectorized_aggregation']
    
    print(f"  Original Iterator: {orig_agg['throughput']:>10,.0f} ticks/s")
    print(f"  Vectorized Numpy:  {vec_agg['throughput']:>10,.0f} ticks/s")
    print(f"  Aggregation Speedup: {vec_agg['speedup']:>8.1f}x")
    
    # Overall improvement
    total_original_time = orig_loading['time'] + orig_agg['time']
    total_optimized_time = opt_loading['time'] + vec_agg['time']
    overall_speedup = total_original_time / total_optimized_time
    
    print(f"\n🏆 Overall Pipeline:")
    print(f"  Original Total:   {total_original_time:>10.3f}s")
    print(f"  Optimized Total:  {total_optimized_time:>10.3f}s")
    print(f"  Overall Speedup:  {overall_speedup:>10.1f}x")
    
    # Performance tier
    if overall_speedup > 20:
        tier = "🏆 EXCEPTIONAL"
    elif overall_speedup > 10:
        tier = "🚀 EXCELLENT"
    elif overall_speedup > 5:
        tier = "✅ VERY GOOD"
    elif overall_speedup > 2:
        tier = "👍 GOOD"
    else:
        tier = "⚠️ MODEST"
    
    print(f"  Performance Tier: {tier}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark data processing performance')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--tick-size', type=float, default=10.0, help='Tick size')
    parser.add_argument('--bucket-ms', type=int, default=50, help='Aggregation bucket size')
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"❌ Error: File not found: {args.input}")
        return
    
    print(f"🎯 Benchmarking: {args.input}")
    print(f"📏 Tick size: {args.tick_size}")
    print(f"⏱️ Bucket size: {args.bucket_ms}ms")
    
    try:
        # Run benchmarks
        loading_results = benchmark_data_loading(args.input, args.tick_size)
        aggregation_results = benchmark_aggregation(args.input, args.tick_size, args.bucket_ms)
        
        # Print summary
        print_summary(loading_results, aggregation_results)
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
