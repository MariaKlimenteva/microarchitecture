import numpy as np
import matplotlib.pyplot as plt
import os

# Parameters
perf = np.linspace(0.1, 3.6, 1000)
# IPC: E=1, P=2
# C_dyn: E=1, P=4
# U(f) = max(1, f + 0.2)

# E-core
f_E = perf / 1.0
V_E = np.maximum(1, f_E + 0.2)
Power_E = 1 * (V_E**2) * f_E

# P-core
f_P = perf / 2.0
V_P = np.maximum(1, f_P + 0.2)
Power_P = 4 * (V_P**2) * f_P

# Optimal execution: choose the core with minimum power for given performance
Power_Optimal = np.minimum(Power_E, Power_P)

# Intersection point calculation
# (Perf + 0.2)^2 * Perf = 2 * (Perf/2 + 0.2)^2 * Perf (for Perf > 0.8 and Perf/2 < 0.8)
# If Perf < 1.6, V_P = 1. So (Perf + 0.2)^2 * Perf = 2 * 1^2 * Perf / 2 * 2 (Wait, P_P calculation above is correct)
# P_P = 4 * V_P^2 * (Perf/2) = 2 * V_P^2 * Perf.
# If Perf <= 1.6, V_P = 1, so P_P = 2 * Perf.
# Intersection: (Perf + 0.2)^2 = 2 => Perf = sqrt(2) - 0.2 approx 1.214
intersect_perf = np.sqrt(2) - 0.2
intersect_power = 2 * intersect_perf

# Plotting
plt.figure(figsize=(10, 7))
plt.plot(perf, Power_E, label='E-core (Efficient)', color='green', linestyle='--', alpha=0.6)
plt.plot(perf, Power_P, label='P-core (Performance)', color='red', linestyle='--', alpha=0.6)
plt.plot(perf, Power_Optimal, label='Optimal Heterogeneous Curve', color='blue', linewidth=2.5)

# Highlight intersection
plt.plot(intersect_perf, intersect_power, 'ko')
plt.annotate(f'Switching point\nPerf ~ {intersect_perf:.2f}', 
             xy=(intersect_perf, intersect_power), xytext=(intersect_perf+0.4, intersect_power-1),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6))

plt.title('Power vs Performance for Heterogeneous Architecture')
plt.xlabel('Performance (dimensionless relative units)')
plt.ylabel('Power (dimensionless relative units)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Labels for regions
plt.text(0.5, 2, 'E-core is more efficient', color='green', fontweight='bold')
plt.text(2.2, 12, 'P-core is more efficient', color='red', fontweight='bold')

plt.tight_layout()
output_path = os.path.join(os.path.dirname(__file__), 'hw1_graphs.png')
plt.savefig(output_path, dpi=300)
print(f"Graph saved to {output_path}")