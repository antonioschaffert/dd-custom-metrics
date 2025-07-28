# PClaims Demo - Datadog Metrics with Namespace

This demo showcases the comprehensive capabilities of the `dd-custom-metrics` package with the `pclaims_demo` namespace.

## 🚀 What the Demo Shows

### 1. **User Registration Simulation**
- Simulates 10 user registrations with 90% success rate
- Tracks different user plans (basic, premium, enterprise)
- Monitors registration sources (web, mobile, api)
- Tracks user countries and profile completion rates
- Sends metrics with rich tagging for analysis

### 2. **Airflow Task Latency Instrumentation**
- **User Processing Task**: Simulates processing user data with 5 steps
- **Data Sync Task**: Simulates external data synchronization
- **Task Execution Counter**: Tracks task execution frequency
- All tasks use `@instrument_latency` decorator to automatically measure execution time

### 3. **Business Metrics**
- Daily revenue tracking
- Order processing metrics
- Average order value calculations
- Customer satisfaction scores

## 📊 Metrics Sent to Datadog

### User Metrics (pclaims_demo.*)
- `pclaims_demo.user.registration` - Counter for user registrations
- `pclaims_demo.user.profile_completion` - Gauge for profile completion percentage
- `pclaims_demo.user.total_count` - Gauge for total user count
- `pclaims_demo.user.success_rate` - Gauge for registration success rate

### Airflow Metrics (pclaims_demo.*)
- `pclaims_demo.airflow.task.latency` - Histogram for task execution times
- `pclaims_demo.airflow.task.executions` - Counter for task executions

### Business Metrics (pclaims_demo.*)
- `pclaims_demo.revenue.daily` - Gauge for daily revenue
- `pclaims_demo.orders.processed` - Counter for processed orders
- `pclaims_demo.order.average_value` - Histogram for average order values
- `pclaims_demo.customer.satisfaction` - Gauge for customer satisfaction

## 🏷️ Tags Used for Filtering

### Environment Tags
- `env:demo` - Identifies demo environment
- `service:user_registration` - User registration service
- `service:business_metrics` - Business metrics service

### User Registration Tags
- `plan:basic|premium|enterprise` - User subscription plan
- `source:web|mobile|api` - Registration source
- `country:US|CA|UK|DE|AU` - User country
- `status:success|failed` - Registration status

### Airflow Tags
- `dag:user_processing` - User processing DAG
- `dag:data_sync` - Data sync DAG
- `dag:demo_pipeline` - Demo pipeline DAG
- `task:process_users` - User processing task
- `task:sync_external_data` - Data sync task

## 🔍 How to View in Datadog

1. **Go to Metrics Explorer**
2. **Search for metrics starting with `pclaims_demo.`**
3. **Filter by tags**:
   - `env:demo` for all demo metrics
   - `service:user_registration` for user metrics
   - `service:business_metrics` for business metrics
   - `dag:*` for Airflow metrics

## 📈 Expected Results

### User Registration
- 10 registration attempts
- ~9 successful registrations (90% success rate)
- Various user plans and sources distributed

### Airflow Tasks
- User Processing Task: ~5-10 seconds total execution time
- Data Sync Task: ~8-15 seconds total execution time
- Task Execution Counter: 1 execution

### Business Metrics
- Daily Revenue: $5,000-$15,000
- Orders Processed: 100-500
- Average Order Value: $20-$40
- Customer Satisfaction: 4.0-5.0

## 🎯 Key Features Demonstrated

1. **Namespace Prefixing**: All metrics prefixed with `pclaims_demo.`
2. **Rich Tagging**: Multiple tags for detailed filtering and analysis
3. **Latency Instrumentation**: Automatic timing of Airflow tasks
4. **Counter Metrics**: Tracking of events and executions
5. **Gauge Metrics**: Current state values (user count, revenue)
6. **Histogram Metrics**: Distribution of values (order amounts, task times)
7. **Error Handling**: Graceful handling of metric sending failures

## 🚀 Running the Demo

```bash
# Make sure your API keys are set
export DD_API_KEY="your_api_key"
export DD_APP_KEY="your_app_key"

# Run the demo
python3 examples/pclaims_demo.py
```

The demo will run for approximately 30-60 seconds and send all metrics to your Datadog account. 