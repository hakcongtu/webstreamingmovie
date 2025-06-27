#!/usr/bin/env python3
"""
Performance Testing Script
Test the performance improvements of the optimized Movie API
"""
import asyncio
import aiohttp
import time
import statistics
import json
from typing import List, Dict, Any
import sys

class PerformanceTester:
    """Performance testing utility"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
    
    async def test_endpoint(self, endpoint: str, method: str = "GET", params: Dict = None, iterations: int = 10) -> Dict[str, Any]:
        """Test a single endpoint"""
        times = []
        errors = 0
        
        async with aiohttp.ClientSession() as session:
            for i in range(iterations):
                start_time = time.time()
                try:
                    if method == "GET":
                        async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                            await response.json()
                    elif method == "POST":
                        async with session.post(f"{self.base_url}{endpoint}", json=params) as response:
                            await response.json()
                    
                    end_time = time.time()
                    times.append(end_time - start_time)
                    
                except Exception as e:
                    errors += 1
                    print(f"Error testing {endpoint}: {e}")
        
        if times:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "min_time": min(times),
                "max_time": max(times),
                "avg_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                "success_rate": (iterations - errors) / iterations * 100
            }
        else:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "success_rate": 0
            }
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance tests"""
        print("🚀 Starting Performance Tests...")
        print("=" * 60)
        
        # Test endpoints
        test_cases = [
            # Basic endpoints
            ("/health", "GET"),
            ("/info", "GET"),
            ("/api/performance/stats", "GET"),
            
            # Movie endpoints
            ("/api/movies/", "GET", {"page": 1, "limit": 10}),
            ("/api/movies/", "GET", {"page": 1, "limit": 50}),
            ("/api/movies/1", "GET"),
            ("/api/movies/100", "GET"),
            
            # Search endpoints
            ("/api/movies/search/", "GET", {"title": "action"}),
            ("/api/movies/search/", "GET", {"genre": "Action", "min_rating": 4.0}),
            ("/api/movies/search/", "GET", {"year": 2020, "max_rating": 5.0}),
            
            # Genre endpoints
            ("/api/movies/genre/Action", "GET", {"page": 1, "limit": 10}),
            ("/api/genres/", "GET"),
            
            # Special endpoints
            ("/api/movies/highly-rated/", "GET", {"page": 1, "limit": 10}),
            ("/api/movies/popular/", "GET", {"page": 1, "limit": 10}),
            ("/api/movies/recent/", "GET", {"page": 1, "limit": 10}),
        ]
        
        results = []
        for test_case in test_cases:
            if len(test_case) == 2:
                endpoint, method = test_case
                params = None
            else:
                endpoint, method, params = test_case
            
            print(f"Testing {method} {endpoint}...")
            result = await self.test_endpoint(endpoint, method, params, iterations=20)
            results.append(result)
            
            # Print result
            if result["success_rate"] > 0:
                print(f"  ✅ Avg: {result['avg_time']:.3f}s, Min: {result['min_time']:.3f}s, Max: {result['max_time']:.3f}s")
            else:
                print(f"  ❌ Failed: {result['errors']} errors")
        
        # Calculate summary statistics
        successful_results = [r for r in results if r["success_rate"] > 0]
        
        if successful_results:
            avg_times = [r["avg_time"] for r in successful_results]
            summary = {
                "total_tests": len(results),
                "successful_tests": len(successful_results),
                "failed_tests": len(results) - len(successful_results),
                "overall_avg_time": statistics.mean(avg_times),
                "overall_min_time": min(avg_times),
                "overall_max_time": max(avg_times),
                "fastest_endpoint": min(successful_results, key=lambda x: x["avg_time"]),
                "slowest_endpoint": max(successful_results, key=lambda x: x["avg_time"]),
                "detailed_results": results
            }
        else:
            summary = {
                "total_tests": len(results),
                "successful_tests": 0,
                "failed_tests": len(results),
                "error": "All tests failed"
            }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print performance test summary"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        if "error" in summary:
            print(f"❌ {summary['error']}")
            return
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['successful_tests']/summary['total_tests']*100:.1f}%")
        print()
        
        print(f"Overall Average Response Time: {summary['overall_avg_time']:.3f}s")
        print(f"Overall Min Response Time: {summary['overall_min_time']:.3f}s")
        print(f"Overall Max Response Time: {summary['overall_max_time']:.3f}s")
        print()
        
        print("🏆 Fastest Endpoint:")
        fastest = summary['fastest_endpoint']
        print(f"  {fastest['method']} {fastest['endpoint']}")
        print(f"  Average: {fastest['avg_time']:.3f}s")
        print()
        
        print("🐌 Slowest Endpoint:")
        slowest = summary['slowest_endpoint']
        print(f"  {slowest['method']} {slowest['endpoint']}")
        print(f"  Average: {slowest['avg_time']:.3f}s")
        print()
        
        # Performance rating
        avg_time = summary['overall_avg_time']
        if avg_time < 0.1:
            rating = "🚀 EXCELLENT"
        elif avg_time < 0.3:
            rating = "✅ GOOD"
        elif avg_time < 0.5:
            rating = "⚠️  ACCEPTABLE"
        else:
            rating = "❌ NEEDS IMPROVEMENT"
        
        print(f"Performance Rating: {rating}")
        print(f"Average Response Time: {avg_time:.3f}s")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS")
        print("-" * 60)
        for result in summary['detailed_results']:
            if result['success_rate'] > 0:
                status = "✅"
            else:
                status = "❌"
            
            print(f"{status} {result['method']} {result['endpoint']}")
            if result['success_rate'] > 0:
                print(f"    Avg: {result['avg_time']:.3f}s | Min: {result['min_time']:.3f}s | Max: {result['max_time']:.3f}s")
                print(f"    Success Rate: {result['success_rate']:.1f}%")
            else:
                print(f"    Errors: {result['errors']}")
            print()

async def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🎬 Movie API Performance Tester")
    print(f"Testing against: {base_url}")
    print()
    
    tester = PerformanceTester(base_url)
    
    try:
        summary = await tester.run_performance_tests()
        tester.print_summary(summary)
        
        # Save results to file
        with open("performance_test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print("💾 Results saved to performance_test_results.json")
        
    except Exception as e:
        print(f"❌ Error running performance tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 