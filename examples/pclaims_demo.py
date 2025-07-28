#!/usr/bin/env python3
"""
PClaims Demo - Comprehensive demonstration of dd-custom-metrics with namespace.
"""

import os
import time
import random
from datetime import datetime
from dd_custom_metrics import DatadogMetrics, instrument_latency, instrument_counter


def simulate_user_registration():
    """Simulate user registration with various metrics."""
    print("=== User Registration Simulation ===")
    
    # Initialize metrics with pclaims_demo namespace
    metrics = DatadogMetrics(
        api_key=os.getenv("DD_API_KEY"),
        app_key=os.getenv("DD_APP_KEY"),
        namespace="pclaims_demo",
        tags=["env:demo", "service:user_registration"]
    )
    
    # Simulate different user registration scenarios
    registration_scenarios = [
        {"plan": "basic", "source": "web", "country": "US"},
        {"plan": "premium", "source": "mobile", "country": "CA"},
        {"plan": "enterprise", "source": "api", "country": "UK"},
        {"plan": "basic", "source": "web", "country": "DE"},
        {"plan": "premium", "source": "mobile", "country": "AU"},
    ]
    
    total_users = 0
    successful_registrations = 0
    failed_registrations = 0
    
    for i in range(10):  # Simulate 10 registrations
        scenario = random.choice(registration_scenarios)
        
        # Simulate registration success/failure
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            successful_registrations += 1
            total_users += 1
            
            # Send registration metrics
            metrics.increment("user.registration", tags=[
                f"plan:{scenario['plan']}",
                f"source:{scenario['source']}",
                f"country:{scenario['country']}",
                "status:success"
            ])
            
            # Simulate user profile completion
            profile_completion = random.randint(50, 100)
            metrics.gauge("user.profile_completion", profile_completion, tags=[
                f"plan:{scenario['plan']}",
                f"source:{scenario['source']}"
            ])
            
            print(f"✅ User {i+1} registered successfully - Plan: {scenario['plan']}, Source: {scenario['source']}")
            
        else:
            failed_registrations += 1
            
            # Send failure metrics
            metrics.increment("user.registration", tags=[
                f"plan:{scenario['plan']}",
                f"source:{scenario['source']}",
                f"country:{scenario['country']}",
                "status:failed"
            ])
            
            print(f"❌ User {i+1} registration failed - Plan: {scenario['plan']}, Source: {scenario['source']}")
        
        # Update total user count
        metrics.gauge("user.total_count", total_users)
        
        # Simulate processing time
        time.sleep(random.uniform(0.1, 0.5))
    
    # Send summary metrics
    metrics.gauge("user.success_rate", (successful_registrations / 10) * 100, tags=["metric_type:summary"])
    metrics.histogram("user.registration_batch_size", 10, tags=["batch:demo"])
    
    print(f"\n📊 Registration Summary:")
    print(f"   Total Attempts: 10")
    print(f"   Successful: {successful_registrations}")
    print(f"   Failed: {failed_registrations}")
    print(f"   Success Rate: {(successful_registrations / 10) * 100:.1f}%")


@instrument_latency("pclaims_demo.airflow.task.latency", tags=["dag:user_processing", "task:process_users"])
def simulate_airflow_user_processing_task():
    """Simulate an Airflow task that processes user data."""
    print("\n=== Airflow User Processing Task ===")
    print("Starting user processing task...")
    
    # Simulate different processing steps
    steps = [
        "validating_user_data",
        "enriching_user_profiles", 
        "sending_welcome_emails",
        "updating_database",
        "generating_reports"
    ]
    
    for step in steps:
        print(f"  Processing: {step}")
        # Simulate variable processing time
        processing_time = random.uniform(0.5, 2.0)
        time.sleep(processing_time)
        print(f"  ✅ Completed: {step} (took {processing_time:.2f}s)")
    
    # Simulate occasional errors
    if random.random() < 0.2:  # 20% chance of error
        print("  ⚠️  Warning: Some users had incomplete data")
        time.sleep(0.5)
    
    print("User processing task completed!")
    return {"processed_users": random.randint(50, 200), "status": "completed"}


@instrument_latency("pclaims_demo.airflow.task.latency", tags=["dag:data_sync", "task:sync_external_data"])
def simulate_airflow_data_sync_task():
    """Simulate an Airflow task that syncs external data."""
    print("\n=== Airflow Data Sync Task ===")
    print("Starting external data sync...")
    
    # Simulate data sync operations
    sync_operations = [
        "connecting_to_external_api",
        "fetching_user_data",
        "validating_data_integrity",
        "transforming_data",
        "loading_to_warehouse"
    ]
    
    for operation in sync_operations:
        print(f"  Syncing: {operation}")
        # Simulate network delays and processing
        sync_time = random.uniform(1.0, 3.0)
        time.sleep(sync_time)
        print(f"  ✅ Synced: {operation} (took {sync_time:.2f}s)")
    
    print("External data sync completed!")
    return {"synced_records": random.randint(1000, 5000), "status": "completed"}


@instrument_counter("pclaims_demo.airflow.task.executions", tags=["dag:demo_pipeline"])
def simulate_airflow_task_execution():
    """Simulate Airflow task execution with counter metrics."""
    print("\n=== Airflow Task Execution Counter ===")
    
    # Simulate task execution
    execution_time = random.uniform(0.5, 1.5)
    time.sleep(execution_time)
    
    print(f"Task executed successfully in {execution_time:.2f}s")
    return {"execution_id": random.randint(1000, 9999)}


def simulate_business_metrics():
    """Simulate various business metrics."""
    print("\n=== Business Metrics Simulation ===")
    
    metrics = DatadogMetrics(
        api_key=os.getenv("DD_API_KEY"),
        app_key=os.getenv("DD_APP_KEY"),
        namespace="pclaims_demo",
        tags=["env:demo", "service:business_metrics"]
    )
    
    # Simulate revenue metrics
    daily_revenue = random.uniform(5000, 15000)
    metrics.gauge("revenue.daily", daily_revenue, tags=["currency:usd"])
    
    # Simulate order metrics
    orders_processed = random.randint(100, 500)
    metrics.increment("orders.processed", orders_processed, tags=["status:completed"])
    
    # Simulate average order value
    avg_order_value = daily_revenue / orders_processed if orders_processed > 0 else 0
    metrics.histogram("order.average_value", avg_order_value, tags=["currency:usd"])
    
    # Simulate customer satisfaction
    satisfaction_score = random.uniform(4.0, 5.0)
    metrics.gauge("customer.satisfaction", satisfaction_score, tags=["scale:1-5"])
    
    print(f"📈 Business Metrics:")
    print(f"   Daily Revenue: ${daily_revenue:.2f}")
    print(f"   Orders Processed: {orders_processed}")
    print(f"   Average Order Value: ${avg_order_value:.2f}")
    print(f"   Customer Satisfaction: {satisfaction_score:.1f}/5.0")


def simulate_user_registration_cycle(metrics, cycle_count):
    """Simulate user registration for a single cycle."""
    print("=== User Registration Cycle ===")
    
    # Simulate different user registration scenarios
    registration_scenarios = [
        {"plan": "basic", "source": "web", "country": "US"},
        {"plan": "premium", "source": "mobile", "country": "CA"},
        {"plan": "enterprise", "source": "api", "country": "UK"},
        {"plan": "basic", "source": "web", "country": "DE"},
        {"plan": "premium", "source": "mobile", "country": "AU"},
    ]
    
    # Simulate 3-8 registrations per cycle
    num_registrations = random.randint(3, 8)
    successful_registrations = 0
    failed_registrations = 0
    
    for i in range(num_registrations):
        scenario = random.choice(registration_scenarios)
        
        # Simulate registration success/failure
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            successful_registrations += 1
            
            # Send registration metrics
            metrics.increment("user.registration", tags=[
                f"plan:{scenario['plan']}",
                f"source:{scenario['source']}",
                f"country:{scenario['country']}",
                "status:success",
                f"cycle:{cycle_count}"
            ])
            
            # Simulate user profile completion
            profile_completion = random.randint(50, 100)
            metrics.gauge("user.profile_completion", profile_completion, tags=[
                f"plan:{scenario['plan']}",
                f"source:{scenario['source']}",
                f"cycle:{cycle_count}"
            ])
            
        else:
            failed_registrations += 1
            
            # Send failure metrics
            metrics.increment("user.registration", tags=[
                f"plan:{scenario['plan']}",
                f"source:{scenario['source']}",
                f"country:{scenario['country']}",
                "status:failed",
                f"cycle:{cycle_count}"
            ])
    
    # Update total user count (simulate cumulative growth)
    total_users = 1000 + (cycle_count * 50) + successful_registrations
    metrics.gauge("user.total_count", total_users, tags=[f"cycle:{cycle_count}"])
    
    # Send summary metrics
    success_rate = (successful_registrations / num_registrations) * 100 if num_registrations > 0 else 0
    metrics.gauge("user.success_rate", success_rate, tags=["metric_type:summary", f"cycle:{cycle_count}"])
    
    print(f"📊 Cycle {cycle_count} Registration Summary:")
    print(f"   Total Attempts: {num_registrations}")
    print(f"   Successful: {successful_registrations}")
    print(f"   Failed: {failed_registrations}")
    print(f"   Success Rate: {success_rate:.1f}%")


def simulate_business_metrics_cycle(metrics, cycle_count):
    """Simulate business metrics for a single cycle."""
    print("=== Business Metrics Cycle ===")
    
    # Simulate revenue metrics with some variation
    base_revenue = 10000
    revenue_variation = random.uniform(0.8, 1.2)  # ±20% variation
    daily_revenue = base_revenue * revenue_variation
    metrics.gauge("revenue.daily", daily_revenue, tags=["currency:usd", f"cycle:{cycle_count}"])
    
    # Simulate order metrics
    orders_processed = random.randint(80, 120)
    metrics.increment("orders.processed", orders_processed, tags=["status:completed", f"cycle:{cycle_count}"])
    
    # Simulate average order value
    avg_order_value = daily_revenue / orders_processed if orders_processed > 0 else 0
    metrics.histogram("order.average_value", avg_order_value, tags=["currency:usd", f"cycle:{cycle_count}"])
    
    # Simulate customer satisfaction with slight variation
    base_satisfaction = 4.5
    satisfaction_variation = random.uniform(-0.3, 0.3)
    satisfaction_score = max(1.0, min(5.0, base_satisfaction + satisfaction_variation))
    metrics.gauge("customer.satisfaction", satisfaction_score, tags=["scale:1-5", f"cycle:{cycle_count}"])
    
    # Simulate system health metrics
    cpu_usage = random.uniform(30, 70)
    memory_usage = random.uniform(40, 80)
    disk_usage = random.uniform(50, 90)
    
    metrics.gauge("system.cpu_usage", cpu_usage, tags=["metric_type:infrastructure", f"cycle:{cycle_count}"])
    metrics.gauge("system.memory_usage", memory_usage, tags=["metric_type:infrastructure", f"cycle:{cycle_count}"])
    metrics.gauge("system.disk_usage", disk_usage, tags=["metric_type:infrastructure", f"cycle:{cycle_count}"])
    
    print(f"📈 Cycle {cycle_count} Business Metrics:")
    print(f"   Daily Revenue: ${daily_revenue:.2f}")
    print(f"   Orders Processed: {orders_processed}")
    print(f"   Average Order Value: ${avg_order_value:.2f}")
    print(f"   Customer Satisfaction: {satisfaction_score:.1f}/5.0")
    print(f"   System Health - CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%, Disk: {disk_usage:.1f}%")


def main():
    """Run the complete PClaims demo for 10 minutes."""
    print("🚀 PClaims Demo - Datadog Metrics with Namespace")
    print("=" * 60)
    
    # Check if API keys are set
    if not os.getenv("DD_API_KEY") or not os.getenv("DD_APP_KEY"):
        print("❌ Error: DD_API_KEY and DD_APP_KEY environment variables must be set")
        return
    
    print(f"✅ Using namespace: pclaims_demo")
    print(f"✅ API Key: {os.getenv('DD_API_KEY')[:8]}...")
    print(f"✅ App Key: {os.getenv('DD_APP_KEY')[:8]}...")
    print(f"⏱️  Running for 10 minutes...")
    
    # Initialize metrics once
    metrics = DatadogMetrics(
        api_key=os.getenv("DD_API_KEY"),
        app_key=os.getenv("DD_APP_KEY"),
        namespace="pclaims_demo",
        tags=["env:demo", "service:continuous_demo"]
    )
    
    start_time = time.time()
    end_time = start_time + (10 * 60)  # 10 minutes
    cycle_count = 0
    
    try:
        while time.time() < end_time:
            cycle_count += 1
            elapsed = time.time() - start_time
            remaining = end_time - time.time()
            
            print(f"\n🔄 Cycle {cycle_count} - Elapsed: {elapsed/60:.1f}min, Remaining: {remaining/60:.1f}min")
            print("-" * 50)
            
            # Simulate user registrations (every cycle)
            simulate_user_registration_cycle(metrics, cycle_count)
            
            # Simulate Airflow tasks (every 2 cycles)
            if cycle_count % 2 == 0:
                airflow_result1 = simulate_airflow_user_processing_task()
                print(f"   Result: {airflow_result1}")
            
            # Simulate data sync (every 3 cycles)
            if cycle_count % 3 == 0:
                airflow_result2 = simulate_airflow_data_sync_task()
                print(f"   Result: {airflow_result2}")
            
            # Simulate task execution counter (every cycle)
            execution_result = simulate_airflow_task_execution()
            print(f"   Execution ID: {execution_result['execution_id']}")
            
            # Simulate business metrics (every cycle)
            simulate_business_metrics_cycle(metrics, cycle_count)
            
            # Send cycle metrics
            metrics.gauge("demo.cycle_count", cycle_count, tags=["metric_type:progress"])
            metrics.gauge("demo.elapsed_minutes", elapsed / 60, tags=["metric_type:progress"])
            
            # Wait before next cycle (30 seconds between cycles)
            if time.time() < end_time:
                print(f"⏳ Waiting 30 seconds before next cycle...")
                time.sleep(30)
        
        print("\n" + "=" * 60)
        print("🎉 10-minute demo completed successfully!")
        print(f"📊 Total cycles completed: {cycle_count}")
        print(f"⏱️  Total runtime: {(time.time() - start_time) / 60:.1f} minutes")
        print("\n📊 Metrics to look for in Datadog:")
        print("   User Metrics:")
        print("     - pclaims_demo.user.registration")
        print("     - pclaims_demo.user.profile_completion")
        print("     - pclaims_demo.user.total_count")
        print("     - pclaims_demo.user.success_rate")
        print("   Airflow Metrics:")
        print("     - pclaims_demo.airflow.task.latency")
        print("     - pclaims_demo.airflow.task.executions")
        print("   Business Metrics:")
        print("     - pclaims_demo.revenue.daily")
        print("     - pclaims_demo.orders.processed")
        print("     - pclaims_demo.order.average_value")
        print("     - pclaims_demo.customer.satisfaction")
        print("   Demo Progress:")
        print("     - pclaims_demo.demo.cycle_count")
        print("     - pclaims_demo.demo.elapsed_minutes")
        print("\n🔍 Filter by tags: env:demo, service:continuous_demo")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Demo interrupted by user after {cycle_count} cycles")
        print(f"⏱️  Total runtime: {(time.time() - start_time) / 60:.1f} minutes")
    except Exception as e:
        print(f"❌ Demo failed after {cycle_count} cycles: {e}")
        print(f"⏱️  Total runtime: {(time.time() - start_time) / 60:.1f} minutes")


if __name__ == "__main__":
    main() 