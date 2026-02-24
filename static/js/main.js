// JavaScript cho ETC Backend Web Interface

document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const uploadForm = document.getElementById('uploadForm');
    const scanBtn = document.getElementById('scanBtn');
    const previewArea = document.getElementById('previewArea');
    const previewImage = document.getElementById('previewImage');
    const loadingArea = document.getElementById('loadingArea');
    const errorArea = document.getElementById('errorArea');
    const errorContent = document.getElementById('errorContent');

    let selectedFile = null;

    // Drag and drop functionality
    uploadArea.addEventListener('click', () => {
        imageInput.click();
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File input change
    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Handle file selection
    function handleFileSelect(file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showError('Vui lòng chọn file hình ảnh hợp lệ!');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showError('File quá lớn! Vui lòng chọn file nhỏ hơn 10MB.');
            return;
        }

        selectedFile = file;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewArea.style.display = 'block';
            previewArea.classList.add('fade-in-up');
        };
        reader.readAsDataURL(file);

        // Enable scan button
        scanBtn.disabled = false;
        scanBtn.classList.add('pulse');

        // Hide previous results
        hideAllAlerts();
    }

    // Form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!selectedFile) {
            showError('Vui lòng chọn hình ảnh trước!');
            return;
        }

        await scanLicensePlate();
    });

    // Scan license plate
    async function scanLicensePlate() {
        // Show loading
        showLoading();
        hideAllAlerts();

        try {
            const formData = new FormData();
            formData.append('image', selectedFile);

            const response = await fetch('/api/scan/license-plate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            hideLoading();

            if (data.success) {
                showResults(data.data);
            } else {
                showError(data.message || 'Có lỗi xảy ra khi nhận diện biển số');
            }
        } catch (error) {
            hideLoading();
            console.error('Error:', error);
            showError('Không thể kết nối đến server. Vui lòng thử lại!');
        }
    }

    // Show loading state
    function showLoading() {
        loadingArea.style.display = 'block';
        loadingArea.classList.add('fade-in-up');
        scanBtn.disabled = true;
        scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
    }

    // Hide loading state
    function hideLoading() {
        loadingArea.style.display = 'none';
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<i class="fas fa-search"></i> Quét biển số';
        scanBtn.classList.remove('pulse');
    }

    // Show results
    function showResults(data) {
        const autoTollArea = document.getElementById('autoTollArea');
        const autoTollContent = document.getElementById('autoTollContent');
        
        if (!data.license_plates || data.license_plates.length === 0) {
            showError('Không nhận diện được biển số xe nào từ ảnh này');
            return;
        }

        // Hiển thị thông tin chi tiết cho tất cả biển số tìm được
        let html = '';
        
        data.license_plates.forEach((plate, index) => {
            const confidencePercent = (plate.confidence * 100).toFixed(1);
            const scorePercent = (plate.score * 100).toFixed(1);
            const isTopResult = index === 0;
            
            html += `
                <div class="license-plate-result-item ${isTopResult ? 'top-result' : ''} ${plate.vehicle_found ? 'vehicle-found' : ''} mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="license-plate-display">
                                <span class="plate-number">${plate.formatted || plate.license_plate}</span>
                                ${isTopResult ? '<span class="badge bg-success ms-2">Kết quả tốt nhất</span>' : ''}
                                ${plate.vehicle_found ? '<span class="badge bg-info ms-2"><i class="fas fa-database"></i> Có trong hệ thống</span>' : ''}
                            </div>
                            
                            <div class="plate-details mt-2">
                                <small class="text-muted">
                                    <i class="fas fa-chart-line"></i> Tin cậy: <strong>${confidencePercent}%</strong> | 
                                    <i class="fas fa-star"></i> Điểm: <strong>${scorePercent}%</strong> | 
                                    <i class="fas fa-code"></i> Nguồn: <strong>${plate.source}</strong>
                                </small>
                                ${plate.original_text ? `<br><small class="text-muted">Text gốc: "${plate.original_text}"</small>` : ''}
                            </div>
                        </div>
                        
                        <div class="text-end">
                            ${plate.vehicle_found ? 
                                '<span class="badge bg-success"><i class="fas fa-check"></i> Có trong hệ thống</span>' : 
                                '<span class="badge bg-warning"><i class="fas fa-exclamation"></i> Không tìm thấy</span>'
                            }
                        </div>
                    </div>
                    
                    ${plate.account_status ? generateAccountStatusInfo(plate.account_status) : ''}
                    ${plate.vehicle_info ? generateVehicleInfo(plate.vehicle_info) : generateNewVehiclePrompt(plate.license_plate)}
                    
                    ${plate.vehicle_found && plate.vehicle_info ? generateAutoTollButton(plate.license_plate, plate.vehicle_info) : ''}
                </div>
            `;
        });

        // Hiển thị phương thức xử lý
        if (data.processing_method) {
            html += `
                <div class="mt-2">
                    <small class="text-muted">
                        <i class="fas fa-cog"></i> 
                        Phương thức: ${data.processing_method === 'fallback' ? 'Fallback (Demo)' : 'EasyOCR AI'}
                    </small>
                </div>
            `;
        }

        autoTollContent.innerHTML = html;
        autoTollArea.style.display = 'block';
        autoTollArea.classList.add('fade-in-up');
        
        // Scroll to results
        autoTollArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Generate vehicle info HTML
    function generateVehicleInfo(vehicle) {
        let html = `
            <div class="vehicle-info mt-3">
                <div class="vehicle-header">
                    <h5><i class="fas fa-car"></i> Thông tin xe trong hệ thống</h5>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="info-section">
                            <h6><i class="fas fa-user"></i> Chủ xe</h6>
                            <p><strong>Tên:</strong> ${vehicle.owner_name || 'N/A'}</p>
                            <p><strong>SĐT:</strong> ${vehicle.owner_phone || 'N/A'}</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="info-section">
                            <h6><i class="fas fa-car"></i> Thông tin xe</h6>
                            <p><strong>Loại:</strong> ${vehicle.vehicle_type || 'N/A'}</p>
                            <p><strong>Hãng:</strong> ${vehicle.brand || 'N/A'} ${vehicle.model || ''}</p>
                            <p><strong>Màu:</strong> ${vehicle.color || 'N/A'}</p>
                            ${vehicle.year ? `<p><strong>Năm:</strong> ${vehicle.year}</p>` : ''}
                        </div>
                    </div>
                </div>
                
                <div class="balance-display">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="balance-label">Số dư tài khoản ETC</div>
                            <div class="balance-amount">
                                ${formatCurrency(vehicle.account_balance || 0)}
                            </div>
                        </div>
                        <div class="account-status">
                            ${getAccountStatusBadge(vehicle.account_balance || 0)}
                        </div>
                    </div>
                </div>
        `;

        // Hiển thị thống kê nếu có
        if (vehicle.statistics) {
            const stats = vehicle.statistics;
            html += `
                <div class="vehicle-stats mt-3">
                    <h6><i class="fas fa-chart-bar"></i> Thống kê hoạt động</h6>
                    <div class="row text-center">
                        <div class="col-4">
                            <div class="stat-item">
                                <div class="stat-number">${stats.total_transactions}</div>
                                <div class="stat-label">Giao dịch</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="stat-item">
                                <div class="stat-number">${formatCurrency(stats.total_spent)}</div>
                                <div class="stat-label">Đã chi tiêu</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="stat-item">
                                <div class="stat-status ${stats.account_status === 'active' ? 'text-success' : 'text-warning'}">
                                    <i class="fas ${stats.account_status === 'active' ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i>
                                    ${stats.account_status === 'active' ? 'Hoạt động' : 'Cần nạp tiền'}
                                </div>
                                <div class="stat-label">Trạng thái</div>
                            </div>
                        </div>
                    </div>
                    ${stats.last_activity ? `<small class="text-muted">Hoạt động cuối: ${formatDateTime(stats.last_activity)}</small>` : ''}
                </div>
            `;
        }

        // Hiển thị giao dịch gần nhất
        if (vehicle.recent_transactions && vehicle.recent_transactions.length > 0) {
            html += `
                <div class="recent-transactions mt-3">
                    <h6><i class="fas fa-history"></i> Giao dịch gần nhất</h6>
                    <div class="transaction-list">
            `;
            
            vehicle.recent_transactions.slice(0, 3).forEach(trans => {
                const typeIcon = trans.type === 'toll' ? 'fa-road' : trans.type === 'topup' ? 'fa-plus-circle' : 'fa-exchange-alt';
                const typeColor = trans.type === 'toll' ? 'text-danger' : trans.type === 'topup' ? 'text-success' : 'text-primary';
                
                html += `
                    <div class="transaction-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center">
                                <i class="fas ${typeIcon} ${typeColor} me-2"></i>
                                <div>
                                    <div class="transaction-type">${getTransactionTypeName(trans.type)}</div>
                                    <small class="text-muted">${formatDateTime(trans.date)}</small>
                                </div>
                            </div>
                            <div class="text-end">
                                <div class="transaction-amount ${typeColor}">
                                    ${trans.type === 'topup' ? '+' : '-'}${formatCurrency(trans.amount)}
                                </div>
                                <small class="text-muted">Còn: ${formatCurrency(trans.balance_after)}</small>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }

        html += `</div>`;
        return html;
    }

    // Generate auto toll collection button
    function generateAutoTollButton(licensePlate, vehicleInfo) {
        const balance = vehicleInfo.account_balance || 0;
        const canAffordToll = balance >= 50000; // Minimum toll amount
        
        return `
            <div class="auto-toll-section mt-3">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <h6 class="mb-0"><i class="fas fa-road"></i> Thu phí tự động</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label">Chọn trạm thu phí:</label>
                                <select class="form-control" id="autoTollStation_${licensePlate.replace(/[^a-zA-Z0-9]/g, '')}" required>
                                    <option value="">Chọn trạm</option>
                                    <option value="Trạm Cần Thơ" data-amount="50000">Trạm Cần Thơ - 50,000 VND</option>
                                    <option value="Trạm Long Thành" data-amount="60000">Trạm Long Thành - 60,000 VND</option>
                                    <option value="Trạm Biên Hòa" data-amount="45000">Trạm Biên Hòa - 45,000 VND</option>
                                    <option value="Trạm Tân Vạn" data-amount="55000">Trạm Tân Vạn - 55,000 VND</option>
                                    <option value="Trạm Mỹ Thuận" data-amount="40000">Trạm Mỹ Thuận - 40,000 VND</option>
                                </select>
                            </div>
                            <div class="col-md-6 d-flex align-items-end">
                                <button 
                                    type="button" 
                                    class="btn btn-success btn-lg w-100" 
                                    onclick="processAutoToll('${licensePlate}')"
                                    ${!canAffordToll ? 'disabled' : ''}
                                    id="autoTollBtn_${licensePlate.replace(/[^a-zA-Z0-9]/g, '')}"
                                >
                                    <i class="fas fa-money-bill-wave"></i> Thu phí ngay
                                </button>
                            </div>
                        </div>
                        ${!canAffordToll ? `
                            <div class="alert alert-warning mt-3 mb-0">
                                <i class="fas fa-exclamation-triangle"></i>
                                <strong>Không đủ tiền để thu phí</strong> - Số dư hiện tại: ${formatCurrency(balance)}
                            </div>
                        ` : `
                            <div class="alert alert-info mt-3 mb-0">
                                <i class="fas fa-info-circle"></i>
                                Số dư hiện tại: <strong>${formatCurrency(balance)}</strong>
                            </div>
                        `}
                    </div>
                </div>
            </div>
        `;
    }

    // Process automatic toll collection
    window.processAutoToll = async function(licensePlate) {
        const cleanPlate = licensePlate.replace(/[^a-zA-Z0-9]/g, '');
        const stationSelect = document.getElementById(`autoTollStation_${cleanPlate}`);
        const tollBtn = document.getElementById(`autoTollBtn_${cleanPlate}`);
        
        if (!stationSelect.value) {
            alert('Vui lòng chọn trạm thu phí!');
            return;
        }
        
        const selectedOption = stationSelect.options[stationSelect.selectedIndex];
        const tollStation = selectedOption.value;
        const tollAmount = parseInt(selectedOption.dataset.amount);
        
        // Confirm toll collection
        const confirmMsg = `Xác nhận thu phí:\n\nBiển số: ${licensePlate}\nTrạm: ${tollStation}\nSố tiền: ${formatCurrency(tollAmount)}\n\nTiếp tục?`;
        if (!confirm(confirmMsg)) {
            return;
        }
        
        // Disable button and show loading
        tollBtn.disabled = true;
        tollBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
        
        try {
            const response = await fetch('/api/transactions/toll', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    license_plate: licensePlate,
                    amount: tollAmount,
                    toll_station: tollStation,
                    description: `Thu phí tự động tại ${tollStation}`
                })
            });
            
            const result = await response.json();
            
            console.log('Toll response:', result); // Debug log
            
            if (result.success) {
                console.log('Balance after:', result.data.balance_after); // Debug log
                // Show success message
                const successMsg = `
                    <div class="alert alert-success mt-3">
                        <h6><i class="fas fa-check-circle"></i> Thu phí thành công!</h6>
                        <p class="mb-1"><strong>Biển số:</strong> ${licensePlate}</p>
                        <p class="mb-1"><strong>Trạm:</strong> ${tollStation}</p>
                        <p class="mb-1"><strong>Số tiền:</strong> ${formatCurrency(tollAmount)}</p>
                        <p class="mb-1"><strong>Số dư còn lại:</strong> ${formatCurrency(result.data.balance_after)}</p>
                        <small class="text-muted">Giao dịch #${result.data.transaction_id}</small>
                    </div>
                `;
                
                // Add success message to the auto toll section
                const autoTollSection = tollBtn.closest('.auto-toll-section');
                const existingAlert = autoTollSection.querySelector('.alert-success');
                if (existingAlert) {
                    existingAlert.remove();
                }
                autoTollSection.insertAdjacentHTML('beforeend', successMsg);
                
                // Reset button
                tollBtn.disabled = false;
                tollBtn.innerHTML = '<i class="fas fa-money-bill-wave"></i> Thu phí ngay';
                stationSelect.value = '';
                
                // Update vehicle balance display if available
                const balanceDisplay = document.querySelector('.balance-amount');
                if (balanceDisplay) {
                    balanceDisplay.textContent = formatCurrency(result.data.balance_after);
                }
                
            } else {
                alert(`Lỗi thu phí: ${result.message}`);
                tollBtn.disabled = false;
                tollBtn.innerHTML = '<i class="fas fa-money-bill-wave"></i> Thu phí ngay';
            }
            
        } catch (error) {
            console.error('Error processing toll:', error);
            alert(`Lỗi kết nối: ${error.message}`);
            tollBtn.disabled = false;
            tollBtn.innerHTML = '<i class="fas fa-money-bill-wave"></i> Thu phí ngay';
        }
    };

    // Get account status badge
    function getAccountStatusBadge(balance) {
        if (balance >= 100000) {
            return '<span class="badge bg-success"><i class="fas fa-check-circle"></i> Đủ tiền</span>';
        } else if (balance >= 50000) {
            return '<span class="badge bg-warning"><i class="fas fa-exclamation-triangle"></i> Sắp hết</span>';
        } else if (balance > 0) {
            return '<span class="badge bg-danger"><i class="fas fa-exclamation-circle"></i> Ít tiền</span>';
        } else {
            return '<span class="badge bg-dark"><i class="fas fa-times-circle"></i> Hết tiền</span>';
        }
    }

    // Get transaction type name
    function getTransactionTypeName(type) {
        const names = {
            'toll': 'Thu phí',
            'topup': 'Nạp tiền',
            'refund': 'Hoàn tiền'
        };
        return names[type] || type;
    }

    // Generate account status info
    function generateAccountStatusInfo(accountStatus) {
        const status = accountStatus.status;
        const balance = accountStatus.balance;
        const canTravel = accountStatus.can_travel;
        
        let statusClass = 'success';
        let statusIcon = 'check-circle';
        let statusText = 'Đủ tiền';
        let actionText = '';
        
        if (status === 'low') {
            statusClass = 'warning';
            statusIcon = 'exclamation-triangle';
            statusText = 'Sắp hết tiền';
            actionText = 'Nên nạp thêm tiền';
        } else if (status === 'empty') {
            statusClass = 'danger';
            statusIcon = 'times-circle';
            statusText = 'Hết tiền';
            actionText = 'Cần nạp tiền ngay';
        }
        
        return `
            <div class="account-status-info mt-2">
                <div class="alert alert-${statusClass} mb-0 py-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-${statusIcon}"></i>
                            <strong>${statusText}</strong>
                            ${actionText ? ` - ${actionText}` : ''}
                        </div>
                        <div class="text-end">
                            <strong>${formatCurrency(balance)}</strong>
                            ${!canTravel ? '<br><small class="text-danger">Không thể đi qua trạm thu phí</small>' : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Generate new vehicle prompt
    function generateNewVehiclePrompt(licensePlate) {
        return `
            <div class="new-vehicle-prompt mt-3">
                <div class="alert alert-info">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-info-circle"></i>
                            <strong>Xe chưa có trong hệ thống</strong>
                            <br><small>Biển số "${licensePlate}" chưa được đăng ký</small>
                        </div>
                        <div>
                            <button class="btn btn-primary btn-sm" onclick="promptAddVehicle('${licensePlate}')">
                                <i class="fas fa-plus"></i> Đăng ký xe
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Format date time
    function formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Prompt to add new vehicle
    window.promptAddVehicle = function(licensePlate) {
        const confirmed = confirm(`Bạn có muốn đăng ký xe với biển số "${licensePlate}" vào hệ thống không?`);
        if (confirmed) {
            // Redirect to vehicle registration or open modal
            window.open(`/swagger/#/vehicles/post_api_vehicles?license_plate=${encodeURIComponent(licensePlate)}`, '_blank');
        }
    };

    // Show error
    function showError(message) {
        errorContent.innerHTML = `<p class="mb-0">${message}</p>`;
        errorArea.style.display = 'block';
        errorArea.classList.add('fade-in-up');
        hideLoading();
    }

    // Hide all alerts
    function hideAllAlerts() {
        const autoTollArea = document.getElementById('autoTollArea');
        const errorArea = document.getElementById('errorArea');
        
        if (autoTollArea) {
            autoTollArea.style.display = 'none';
            autoTollArea.classList.remove('fade-in-up');
        }
        
        if (errorArea) {
            errorArea.style.display = 'none';
            errorArea.classList.remove('fade-in-up');
        }
    }

    // Format currency
    function formatCurrency(amount) {
        // Handle undefined, null, or non-numeric values
        if (amount === undefined || amount === null || isNaN(amount)) {
            return '0 ₫';
        }
        
        // Convert to number if it's a string
        const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
        
        if (isNaN(numAmount)) {
            return '0 ₫';
        }
        
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(numAmount);
    }

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add some interactive effects
    document.querySelectorAll('.feature-card, .api-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Console welcome message
    console.log(`
    🚀 ETC Backend Web Interface
    ============================
    Version: 1.0.0
    Environment: ${document.querySelector('footer strong')?.textContent || 'Unknown'}
    
    Available APIs:
    - /api/vehicles
    - /api/transactions  
    - /api/scan
    - /api/health
    
    📖 API Documentation: /swagger/
    `);
});

// Utility functions
window.ETCUtils = {
    // Format license plate for display
    formatLicensePlate: function(plate) {
        if (!plate) return '';
        return plate.toUpperCase().replace(/\s+/g, '');
    },
    
    // Validate license plate format
    isValidLicensePlate: function(plate) {
        const patterns = [
            /^\d{2}[A-Z]\d{5}$/,  // 30G12345
            /^\d{2}[A-Z]{2}\d{4}$/, // 29AB1234
            /^\d{2}[A-Z]\d{4}$/   // 51F1234
        ];
        
        return patterns.some(pattern => pattern.test(plate));
    },
    
    // Get vehicle type icon
    getVehicleIcon: function(type) {
        const icons = {
            'Car': 'fas fa-car',
            'Motorcycle': 'fas fa-motorcycle', 
            'Truck': 'fas fa-truck',
            'Bus': 'fas fa-bus'
        };
        return icons[type] || 'fas fa-car';
    }
};
