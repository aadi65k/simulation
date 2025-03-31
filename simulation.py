import simpy
import random
import matplotlib.pyplot as plt
from packet import Packet
from typing import List, Tuple
import logging
import json
import csv
from datetime import datetime

class NetworkSimulator:
    def __init__(self, env: simpy.Environment, error_rate: float = 0.1):
        # Setup logging
        logging.basicConfig(
            filename=f'network_simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.env = env
        self.error_rate = error_rate
        self.latency_data: List[float] = []
        self.packet_loss: List[bool] = []
        self.successful_transmissions = 0
        self.total_transmissions = 0
        self.adaptive_window = 10  # Window size for adaptive error rate
        self.min_error_rate = 0.05
        self.max_error_rate = 0.5

    def adjust_error_rate(self):
        if len(self.packet_loss) >= self.adaptive_window:
            recent_loss_rate = sum(self.packet_loss[-self.adaptive_window:]) / self.adaptive_window
            if recent_loss_rate > 0.3:  # Too many losses
                self.error_rate = max(self.min_error_rate, self.error_rate * 0.8)
            elif recent_loss_rate < 0.1:  # Too few losses
                self.error_rate = min(self.max_error_rate, self.error_rate * 1.2)
            logging.info(f"Adjusted error rate to {self.error_rate:.3f}")

    def corrupt_data(self, data: bytes) -> bytes:
        if not data:
            logging.warning("Received empty data for corruption")
            return data
        try:
            if random.random() < self.error_rate:
                pos = random.randint(0, len(data) - 1)
                corrupted = bytearray(data)
                corrupted[pos] ^= random.randint(1, 255)
                logging.debug(f"Data corrupted at position {pos}")
                return bytes(corrupted)
            return data
        except Exception as e:
            logging.error(f"Error in data corruption: {str(e)}")
            return data

    def transmit(self, packet: Packet):
        try:
            yield self.env.timeout(random.uniform(0.1, 0.5))
            
            start_time = self.env.now
            encoded_data = packet.encode()
            
            if not encoded_data:
                logging.error("Empty packet data received")
                raise ValueError("Empty packet data")
            
            corrupted_data = self.corrupt_data(encoded_data)
            decoded_data = packet.decode(corrupted_data)
            
            latency = self.env.now - start_time
            self.latency_data.append(latency)
            self.packet_loss.append(decoded_data is None)
            
            self.total_transmissions += 1
            if decoded_data is not None:
                self.successful_transmissions += 1
            
            self.adjust_error_rate()
            self.save_statistics()

        except Exception as e:
            logging.error(f"Transmission error: {str(e)}")
            self.packet_loss.append(True)
            self.total_transmissions += 1

    def save_statistics(self):
        stats = self.get_statistics()
        
        # Save as JSON
        with open('simulation_stats.json', 'w') as f:
            json.dump(stats, f, indent=4)
        
        # Save as CSV
        with open('simulation_stats.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:  # Write header if file is empty
                writer.writerow(stats.keys())
            writer.writerow(stats.values())

    def plot_metrics(self):
        if not self.latency_data:
            print("No data to plot")
            return

        plt.figure(figsize=(12, 4))
        
        # Plot latency
        plt.subplot(121)
        plt.plot(self.latency_data)
        plt.title('Transmission Latency')
        plt.xlabel('Packet Number')
        plt.ylabel('Latency (s)')
        
        # Add average latency annotation
        avg_latency = sum(self.latency_data) / len(self.latency_data)
        plt.text(0.02, 0.95, f'Avg Latency: {avg_latency:.3f}s',
                transform=plt.gca().transAxes)
        
        # Plot packet loss
        plt.subplot(122)
        loss_rate = sum(self.packet_loss) / len(self.packet_loss)
        success_rate = 1 - loss_rate
        plt.bar(['Success', 'Loss'], [success_rate, loss_rate])
        plt.title('Packet Loss Rate')
        plt.ylabel('Rate')
        
        # Add detailed statistics
        stats_text = (
            f'Total Packets: {self.total_transmissions}\n'
            f'Success Rate: {success_rate:.1%}\n'
            f'Loss Rate: {loss_rate:.1%}'
        )
        plt.text(0.02, 0.95, stats_text,
                transform=plt.gca().transAxes,
                verticalalignment='top')
        
        plt.tight_layout()
        plt.show()

    def get_statistics(self) -> dict:
        if not self.latency_data:
            return {"error": "No data available"}
            
        return {
            "total_transmissions": self.total_transmissions,
            "successful_transmissions": self.successful_transmissions,
            "average_latency": sum(self.latency_data) / len(self.latency_data),
            "loss_rate": sum(self.packet_loss) / len(self.packet_loss),
            "current_error_rate": self.error_rate
        }