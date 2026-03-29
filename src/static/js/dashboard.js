        // Chart.js global defaults for sleek UI
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Outfit', sans-serif";
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.9)';
        Chart.defaults.plugins.tooltip.titleColor = '#f8fafc';
        Chart.defaults.plugins.tooltip.bodyColor = '#cbd5e1';
        Chart.defaults.plugins.tooltip.padding = 12;
        Chart.defaults.plugins.tooltip.cornerRadius = 8;
        Chart.defaults.plugins.tooltip.displayColors = false;

        let barChartInstance = null;
        let doughnutChartInstance = null;

        async function fetchAnalytics() {
            try {
                const response = await fetch('/api/analytics');
                const data = await response.json();

                // Animate Numbers
                animateValue('valTotalPlanes', parseInt(document.getElementById('valTotalPlanes').innerText) || 0, data.total_planes, 1000);
                animateValue('valAvgAltitude', parseFloat(document.getElementById('valAvgAltitude').innerText) || 0, data.avg_altitude, 1000);
                animateValue('valAvgVelocity', parseFloat(document.getElementById('valAvgVelocity').innerText) || 0, data.avg_velocity, 1000);

                // Prepare Chart Data
                const originLabels = data.top_countries.map(c => c.country || 'Unknown');
                const originData = data.top_countries.map(c => c.count);
                const statusData = [data.in_air, data.on_ground];

                // Render Bar Chart
                const barCtx = document.getElementById('barChart').getContext('2d');
                if (barChartInstance) {
                    barChartInstance.data.labels = originLabels;
                    barChartInstance.data.datasets[0].data = originData;
                    barChartInstance.update();
                } else {
                    const gradientBar = barCtx.createLinearGradient(0, 0, 0, 400);
                    gradientBar.addColorStop(0, 'rgba(59, 130, 246, 0.7)');
                    gradientBar.addColorStop(1, 'rgba(139, 92, 246, 0.1)');

                    barChartInstance = new Chart(barCtx, {
                        type: 'bar',
                        data: {
                            labels: originLabels,
                            datasets: [{
                                label: 'Number of Planes',
                                data: originData,
                                backgroundColor: gradientBar,
                                borderColor: '#3b82f6',
                                borderWidth: 1,
                                borderRadius: 6,
                                hoverBackgroundColor: '#60a5fa'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false } },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false }
                                },
                                x: { grid: { display: false } }
                            },
                            animation: { duration: 1500, easing: 'easeOutQuart' }
                        }
                    });
                }

                // Render Doughnut Chart
                const doughnutCtx = document.getElementById('doughnutChart').getContext('2d');
                if (doughnutChartInstance) {
                    doughnutChartInstance.data.datasets[0].data = statusData;
                    doughnutChartInstance.update();
                } else {
                    doughnutChartInstance = new Chart(doughnutCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['In Air', 'On Ground'],
                            datasets: [{
                                data: statusData,
                                backgroundColor: ['#10b981', '#f59e0b'],
                                borderColor: '#0b0f19',
                                borderWidth: 4,
                                hoverOffset: 4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            cutout: '75%',
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: { padding: 20, usePointStyle: true, pointStyle: 'circle' }
                                }
                            },
                            animation: { duration: 1500, easing: 'easeOutQuart' }
                        }
                    });
                }

                // Hide loading overlay on first successful fetch
                const overlay = document.getElementById('loadingOverlay');
                if (overlay.style.opacity !== '0') {
                    overlay.style.opacity = '0';
                    setTimeout(() => overlay.style.display = 'none', 500);
                }

            } catch (error) {
                console.error("Failed to fetch analytics data:", error);
            }
        }

        // Simple number counter animation
        function animateValue(id, start, end, duration) {
            const obj = document.getElementById(id);
            if (start === end) {
                obj.innerHTML = end;
                return;
            }
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                // Ease out functionality for smoother finish
                const easeOut = 1 - Math.pow(1 - progress, 3);
                let current = start + (end - start) * easeOut;

                // formatting 
                if (end % 1 !== 0) obj.innerHTML = current.toFixed(2);
                else obj.innerHTML = Math.floor(current);

                if (progress < 1) {
                    window.requestAnimationFrame(step);
                } else {
                    obj.innerHTML = end;
                }
            };
            window.requestAnimationFrame(step);
        }

        // Bootstrap tooltips initialization
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

        // Fetch immediately and then poll every 15 seconds
        window.addEventListener('DOMContentLoaded', () => {
            fetchAnalytics();
            setInterval(fetchAnalytics, 15000);
        });