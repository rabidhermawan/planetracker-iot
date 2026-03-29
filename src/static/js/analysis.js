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
        let pollInterval = null;

        // Master function to fetch both Analytics and Table Data
        async function updateDashboardData() {
            const startDateValue = document.getElementById('startDateFilter').value;
            const endDateValue = document.getElementById('endDateFilter').value;
            
            // Ensure dates are selected
            if (!startDateValue || !endDateValue) {
                alert("Please select both a start date and an end date to view analysis.");
                return;
            }

            // Show loading overlay
            const overlay = document.getElementById('loadingOverlay');
            overlay.style.setProperty('display', 'flex', 'important');
            setTimeout(() => { overlay.style.opacity = '1'; }, 10);
                
            try {
                // Execute fetches in parallel
                await Promise.all([
                    fetchAnalytics(startDateValue, endDateValue), 
                    fetchPlanesList(startDateValue, endDateValue),
                    fetchHeatmapData(startDateValue, endDateValue) // Heatmap is fetched here
                ]);
            } catch (error) {
                console.error("Error fetching data:", error);
                alert("There was an error fetching the data. Please try again.");
            } finally {
                // Hide loading overlay
                overlay.style.opacity = '0';
                setTimeout(() => overlay.style.setProperty('display', 'none', 'important'), 300);
            }
        }
        
        async function fetchAnalytics(startDate, endDate) {
            let apiUrl = `/api/analytics?start_date=${startDate}&end_date=${endDate}`;
            const response = await fetch(apiUrl);
            const data = await response.json();


            // Animate Numbers
            animateValue('valTotalPlanes', parseInt(document.getElementById('valTotalPlanes').innerText) || 0, data.total_planes || 0, 1000);
            animateValue('valAvgAltitude', parseFloat(document.getElementById('valAvgAltitude').innerText) || 0, data.avg_altitude || 0, 1000);
            animateValue('valAvgVelocity', parseFloat(document.getElementById('valAvgVelocity').innerText) || 0, data.avg_velocity || 0, 1000);

            // Prepare Chart Data safely
            const originLabels = (data.top_countries || []).map(c => c.country || 'Unknown');
            const originData = (data.top_countries || []).map(c => c.count || 0);
            const statusData = [data.in_air || 0, data.on_ground || 0];


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

        }
          
        let allPlanesData = [];
        let currentPage = 1;
        const rowsPerPage = 10; // Change this to show more/less rows per page

        async function fetchPlanesList(startDate, endDate) {
            let apiUrl = `/api/planes?start_date=${startDate}&end_date=${endDate}`;
            const response = await fetch(apiUrl);
            
            // Store the fetched data globally instead of rendering immediately
            allPlanesData = await response.json();
            
            // Reset to page 1 whenever new data is fetched
            currentPage = 1; 
            
            // Call the render functions
            renderTable();
            renderPagination();
        }

        function renderTable() {
            const tableBody = document.getElementById('planesTableBody');
            tableBody.innerHTML = '';

            if (allPlanesData.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-secondary py-4">No flights found for this period.</td></tr>`;
                return;
            }

            // Calculate start and end indices for slicing the array
            const startIndex = (currentPage - 1) * rowsPerPage;
            const endIndex = startIndex + rowsPerPage;
            const paginatedData = allPlanesData.slice(startIndex, endIndex);

            paginatedData.forEach(plane => {
                const statusBadge = plane.on_ground 
                    ? `<span class="badge bg-warning text-dark"><i class="bi bi-airplane me-1" style="transform: rotate(90deg); display: inline-block;"></i> Grounded</span>` 
                    : `<span class="badge bg-success"><i class="bi bi-airplane-engines me-1"></i> In Air</span>`;

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="fw-medium text-light">${plane.icao24 || 'N/A'}</td>
                    <td>${plane.callsign || 'N/A'}</td>
                    <td>${plane.origin || 'Unknown'}</td>
                `;
                tableBody.appendChild(tr);
            });
        }

        function renderPagination() {
            const paginationContainer = document.getElementById('paginationControls');
            paginationContainer.innerHTML = '';

            const totalPages = Math.ceil(allPlanesData.length / rowsPerPage);
            
            // Don't show pagination if there's only 1 page of data
            if (totalPages <= 1) return;

            // Common dark theme styles for the buttons
            const defaultClass = "page-link bg-transparent text-secondary border-secondary";
            const activeClass = "page-link bg-primary text-white border-primary";
            const disabledClass = "page-link bg-transparent text-muted border-secondary";

            // Previous Button
            let html = `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                          <a class="${currentPage === 1 ? disabledClass : defaultClass}" href="#" onclick="changePage(${currentPage - 1}); return false;">&laquo; Prev</a>
                        </li>`;

            // Max 5 buttons to not overflow
            let startPage = Math.max(1, currentPage - 2);
            let endPage = Math.min(totalPages, startPage + 4);
            if (endPage - startPage < 4) {
                startPage = Math.max(1, endPage - 4);
            }

            for (let i = startPage; i <= endPage; i++) {
                html += `<li class="page-item ${currentPage === i ? 'active' : ''}">
                           <a class="${currentPage === i ? activeClass : defaultClass}" href="#" onclick="changePage(${i}); return false;">${i}</a>
                         </li>`;
            }

            // Next Button
            html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                       <a class="${currentPage === totalPages ? disabledClass : defaultClass}" href="#" onclick="changePage(${currentPage + 1}); return false;">Next &raquo;</a>
                     </li>`;

            paginationContainer.innerHTML = html;
        }

        // Page clicks
        function changePage(newPage) {
            const totalPages = Math.ceil(allPlanesData.length / rowsPerPage);
            
            // Prevent out-of-bounds clicks
            if (newPage < 1 || newPage > totalPages) return;
            
            currentPage = newPage;
            renderTable();
            renderPagination();
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
        
        // Leaflet map functions
        let analyticsMap = null;
        let heatmapLayer = null;

        function initMap() {
            analyticsMap = L.map('heatmapContainer').setView([20.0, 0.0], 2);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(analyticsMap);
        }

        async function fetchHeatmapData(startDate, endDate) {
            try {
                let apiUrl = `/api/heatmap_data?start_date=${startDate}&end_date=${endDate}`;
                const response = await fetch(apiUrl);
                const heatPoints = await response.json();

                if (heatmapLayer) {
                    analyticsMap.removeLayer(heatmapLayer);
                }

                if (heatPoints && heatPoints.length > 0) {
                    heatmapLayer = L.heatLayer(heatPoints, {
                        radius: 15,
                        blur: 20,
                        maxZoom: 10,
                        gradient: {0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
                    }).addTo(analyticsMap);
                    
                    setTimeout(() => {
                        analyticsMap.invalidateSize();
                    }, 100);
                } else {
                    console.warn("No heatmap data returned for this date range.");
                }
            } catch (error) {
                console.error("Failed to fetch heatmap data:", error);
            }
        }

        // Initialize App
        window.addEventListener('DOMContentLoaded', () => {
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

            initMap();

            // Bind manual fetch to the button click
            document.getElementById('btnFetchData').addEventListener('click', updateDashboardData);
        });