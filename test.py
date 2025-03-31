import simpy
from packet import Packet
from simulation import NetworkSimulator

def test_basic_transmission():
    # Initialize simulation
    env = simpy.Environment()
    simulator = NetworkSimulator(env, error_rate=0.2)
    
    # Test single packet
    test_data = {"message": "Hello, World!", "test_id": 1}
    packet = Packet(test_data)
    env.process(simulator.transmit(packet))
    env.run()
    
    # Verify statistics were recorded
    stats = simulator.get_statistics()
    print("Basic Transmission Test Results:")
    print(f"Total Transmissions: {stats['total_transmissions']}")
    print(f"Success Rate: {1 - stats['loss_rate']:.2%}")
    print(f"Average Latency: {stats['average_latency']:.3f}s")

def test_error_handling():
    # Initialize simulation
    env = simpy.Environment()
    simulator = NetworkSimulator(env, error_rate=0.5)  # High error rate for testing
    
    # Test with various data types
    test_cases = [
        {"message": "Normal message", "test_id": 1},
        {"message": "🌟 Unicode test", "test_id": 2},
        {"message": "a" * 1000, "test_id": 3},  # Large message
    ]
    
    for data in test_cases:
        packet = Packet(data)
        env.process(simulator.transmit(packet))
    
    env.run()
    simulator.plot_metrics()

if __name__ == "__main__":
    print("Running transmission tests...")
    test_basic_transmission()
    print("\nRunning error handling tests...")
    test_error_handling()