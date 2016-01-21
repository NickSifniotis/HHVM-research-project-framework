for file in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
	echo performance > $file
done
echo 1 | sudo tee /proc/sys/net/ipv4/tcp_tw_reuse
