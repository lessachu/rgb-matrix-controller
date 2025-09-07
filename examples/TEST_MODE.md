# MUNI Display Test Mode

The MUNI display system includes a comprehensive test mode that allows you to test different scenarios, error conditions, and animation sequences without relying on the live 511.org API.

## Enabling Test Mode

1. **Edit Configuration**: Set `TEST_MODE=true` in `examples/muni.config`
2. **Run Display**: Execute `python3 examples/muni_l_taraval_live.py`
3. **Observe**: The system will cycle through test data entries

## Test Data Format

Test data is stored in `examples/muni_test.txt` using the same JSON format as the 511.org API responses.

### File Structure
```
# Comments start with #
# Each JSON response should be on a single line
{"ServiceDelivery": {...}}
{"ServiceDelivery": {...}}
```

### Example Test Entry
```json
{"ServiceDelivery":{"ResponseTimestamp":"2025-01-07T10:30:00Z","StopMonitoringDelivery":[{"MonitoredStopVisit":[{"MonitoredVehicleJourney":{"LineRef":"L","DirectionRef":"1","DestinationName":"Embarcadero","MonitoredCall":{"ExpectedArrivalTime":"2025-01-07T10:33:00Z"}}}]}]}}
```

## Included Test Scenarios

The default `muni_test.txt` includes these test scenarios:

1. **Initial Load** - Normal arrival data (3, 8, 15 minutes)
2. **Approaching Train** - Train in 1 minute (red urgency)
3. **Arriving Now** - Train arriving immediately (red urgency)
4. **Next Train** - Previous train departed, next becomes primary
5. **Long Wait** - 15-minute wait (green color)
6. **No Data** - Empty response (error condition)
7. **Service Restored** - Data returns after error
8. **Cycle Repeat** - Returns to initial state

## Test Mode Features

### Visual Indicators
- **🧪 Using test mode data from muni_test.txt** - Startup message
- **📋 Loaded X test data entries** - Shows number of test scenarios
- **📋 Using test data entry X/Y** - Shows current test data position

### Animation Testing
- **Two-phase animations** - Exit and enter sequences
- **Color coding** - Red (urgent), Orange (soon), Green (later)
- **Error handling** - No data scenarios
- **Timing variations** - Different arrival times

### Cycling Behavior
- Test data cycles automatically through all entries
- Returns to first entry after reaching the end
- Each update uses the next test data entry
- Perfect for testing animation sequences

## Creating Custom Test Data

### 1. Add New Scenarios
Edit `muni_test.txt` and add new JSON entries:

```json
# Custom scenario - very long wait
{"ServiceDelivery":{"ResponseTimestamp":"2025-01-07T10:30:00Z","StopMonitoringDelivery":[{"MonitoredStopVisit":[{"MonitoredVehicleJourney":{"LineRef":"L","DirectionRef":"1","DestinationName":"Embarcadero","MonitoredCall":{"ExpectedArrivalTime":"2025-01-07T11:00:00Z"}}}]}]}}
```

### 2. Test Error Conditions
```json
# No arrivals
{"ServiceDelivery":{"ResponseTimestamp":"2025-01-07T10:30:00Z","StopMonitoringDelivery":[{"MonitoredStopVisit":[]}]}}

# API error simulation
{"error": "Service temporarily unavailable"}
```

### 3. Test Different Times
- **0 minutes**: `"ExpectedArrivalTime":"2025-01-07T10:30:00Z"` (NOW)
- **1 minute**: `"ExpectedArrivalTime":"2025-01-07T10:31:00Z"` (Red)
- **5 minutes**: `"ExpectedArrivalTime":"2025-01-07T10:35:00Z"` (Orange)
- **15 minutes**: `"ExpectedArrivalTime":"2025-01-07T10:45:00Z"` (Green)

## Benefits of Test Mode

### Development
- **Rapid Testing** - No API rate limits
- **Predictable Data** - Known test scenarios
- **Error Simulation** - Test error handling
- **Animation Verification** - Consistent timing

### Demonstration
- **Reliable Demo** - No network dependencies
- **Scenario Control** - Show specific features
- **Color Testing** - All urgency levels
- **Professional Presentation** - Smooth operation

### Debugging
- **Consistent Results** - Repeatable test cases
- **Timing Control** - Predictable sequences
- **Edge Cases** - Error conditions
- **Performance Testing** - Animation smoothness

## Disabling Test Mode

Set `TEST_MODE=false` in `examples/muni.config` to return to live data mode.

## File Locations

- **Configuration**: `examples/muni.config`
- **Test Data**: `examples/muni_test.txt`
- **Main Script**: `examples/muni_l_taraval_live.py`
- **Documentation**: `examples/TEST_MODE.md`
