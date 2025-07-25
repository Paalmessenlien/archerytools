// Main JavaScript for Arrow Tuning System

// Global utilities
const ArrowTuning = {
    // Show loading overlay
    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    },

    // Hide loading overlay
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    },

    // Show notification
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification px-4 py-3 rounded-md shadow-lg text-white ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
        }`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span class="text-sm">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white opacity-70 hover:opacity-100">
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto-hide after duration
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, duration);
    },

    // Format number as currency
    formatCurrency(value) {
        if (value == null) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value);
    },

    // Format number with decimal places
    formatNumber(value, decimals = 1) {
        if (value == null) return 'N/A';
        return value.toFixed(decimals);
    },

    // Debounce function for search inputs
    debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },

    // Local storage helpers
    storage: {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn('Could not save to localStorage:', e);
            }
        },

        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.warn('Could not read from localStorage:', e);
                return defaultValue;
            }
        },

        remove(key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.warn('Could not remove from localStorage:', e);
            }
        }
    }
};

// Comparison functionality
const Comparison = {
    items: [],
    maxItems: 5,

    init() {
        this.items = ArrowTuning.storage.get('comparison_items', []);
        this.updateUI();
    },

    add(arrowId) {
        if (this.items.includes(arrowId)) {
            ArrowTuning.showNotification('Arrow is already in comparison list', 'warning');
            return false;
        }

        if (this.items.length >= this.maxItems) {
            ArrowTuning.showNotification(`You can compare up to ${this.maxItems} arrows at once`, 'warning');
            return false;
        }

        this.items.push(arrowId);
        this.save();
        this.updateUI();
        ArrowTuning.showNotification('Arrow added to comparison', 'success');
        return true;
    },

    remove(arrowId) {
        this.items = this.items.filter(id => id !== arrowId);
        this.save();
        this.updateUI();
        ArrowTuning.showNotification('Arrow removed from comparison', 'info');
    },

    clear() {
        this.items = [];
        this.save();
        this.updateUI();
        ArrowTuning.showNotification('Comparison list cleared', 'info');
    },

    save() {
        ArrowTuning.storage.set('comparison_items', this.items);
    },

    updateUI() {
        // Update comparison counter in navigation
        const counters = document.querySelectorAll('.comparison-counter');
        counters.forEach(counter => {
            counter.textContent = this.items.length;
            counter.style.display = this.items.length > 0 ? 'inline' : 'none';
        });

        // Update comparison buttons
        const buttons = document.querySelectorAll('[data-comparison-button]');
        buttons.forEach(button => {
            const arrowId = parseInt(button.dataset.arrowId);
            if (this.items.includes(arrowId)) {
                button.innerHTML = `
                    <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    In Comparison
                `;
                button.disabled = true;
                button.classList.add('opacity-50');
            }
        });

        // Show/hide comparison panel
        this.updateComparisonPanel();
    },

    updateComparisonPanel() {
        const panel = document.getElementById('comparison-panel');
        if (!panel) return;

        if (this.items.length === 0) {
            panel.classList.add('hidden');
            return;
        }

        panel.classList.remove('hidden');
        const itemsContainer = panel.querySelector('.comparison-items');
        if (itemsContainer) {
            itemsContainer.innerHTML = this.items.map(id => `
                <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span class="text-sm">Arrow #${id}</span>
                    <button onclick="Comparison.remove(${id})" class="text-red-500 hover:text-red-700">
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            `).join('');
        }

        const compareButton = panel.querySelector('.compare-button');
        if (compareButton) {
            compareButton.disabled = this.items.length < 2;
        }
    },

    goToComparison() {
        if (this.items.length < 2) {
            ArrowTuning.showNotification('Select at least 2 arrows to compare', 'warning');
            return;
        }

        const url = new URL('/comparison', window.location.origin);
        this.items.forEach(id => url.searchParams.append('arrows', id));
        window.location.href = url.toString();
    }
};

// Search functionality
const Search = {
    init() {
        // Initialize search with debouncing
        const searchInputs = document.querySelectorAll('[data-search]');
        searchInputs.forEach(input => {
            input.addEventListener('input', ArrowTuning.debounce(this.performSearch.bind(this), 300));
        });

        // Initialize filters
        this.initFilters();
    },

    performSearch(event) {
        const query = event.target.value.trim();
        if (query.length < 2 && query.length > 0) {
            return; // Don't search for very short queries
        }

        this.searchArrows(query);
    },

    async searchArrows(query) {
        try {
            ArrowTuning.showLoading();
            
            const params = new URLSearchParams();
            if (query) params.set('q', query);
            params.set('limit', '10');

            const response = await fetch(`/api/search?${params}`);
            const data = await response.json();

            this.displaySearchResults(data.results);
        } catch (error) {
            console.error('Search error:', error);
            ArrowTuning.showNotification('Search failed. Please try again.', 'error');
        } finally {
            ArrowTuning.hideLoading();
        }
    },

    displaySearchResults(results) {
        const container = document.getElementById('search-results');
        if (!container) return;

        if (results.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No results found</p>';
            return;
        }

        container.innerHTML = results.map(arrow => `
            <div class="p-3 border border-gray-200 rounded hover:border-primary-300">
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-medium text-archery-800">
                            <a href="/arrow/${arrow.id}" class="hover:text-primary-600">
                                ${arrow.manufacturer} ${arrow.model_name}
                            </a>
                        </h4>
                        <div class="text-sm text-gray-600 mt-1">
                            Spine: ${arrow.min_spine}${arrow.max_spine !== arrow.min_spine ? `-${arrow.max_spine}` : ''}
                            | ${arrow.spine_count} option${arrow.spine_count !== 1 ? 's' : ''}
                        </div>
                    </div>
                    <button onclick="Comparison.add(${arrow.id})" 
                            class="text-sm text-primary-600 hover:text-primary-700">
                        Add to Compare
                    </button>
                </div>
            </div>
        `).join('');
    },

    initFilters() {
        // Initialize filter dropdowns and range inputs
        const filterForm = document.getElementById('filter-form');
        if (!filterForm) return;

        // Auto-submit form on filter change
        const filterInputs = filterForm.querySelectorAll('select, input[type="number"]');
        filterInputs.forEach(input => {
            input.addEventListener('change', ArrowTuning.debounce(() => {
                filterForm.submit();
            }, 500));
        });
    }
};

// Form validation
const FormValidation = {
    init() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', this.validateForm.bind(this));
        });
    },

    validateForm(event) {
        const form = event.target;
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        if (!isValid) {
            event.preventDefault();
            ArrowTuning.showNotification('Please fill in all required fields', 'error');
        }

        return isValid;
    },

    showFieldError(field, message) {
        field.classList.add('border-red-500');
        
        let errorDiv = field.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('field-error')) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'field-error text-red-500 text-xs mt-1';
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
        errorDiv.textContent = message;
    },

    clearFieldError(field) {
        field.classList.remove('border-red-500');
        
        const errorDiv = field.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains('field-error')) {
            errorDiv.remove();
        }
    }
};

// Analytics (placeholder for future implementation)
const Analytics = {
    track(event, properties = {}) {
        // Placeholder for analytics tracking
        console.log('Analytics event:', event, properties);
    }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize modules
    Comparison.init();
    Search.init();
    FormValidation.init();

    // Add global event listeners
    document.addEventListener('click', function(e) {
        // Handle comparison buttons
        if (e.target.matches('[data-add-comparison]')) {
            e.preventDefault();
            const arrowId = parseInt(e.target.dataset.arrowId);
            Comparison.add(arrowId);
        }

        // Handle external links
        if (e.target.matches('a[href^="http"]:not([href^="' + window.location.origin + '"])')) {
            e.target.setAttribute('target', '_blank');
            e.target.setAttribute('rel', 'noopener noreferrer');
        }
    });

    // Handle keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+K or Cmd+K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('[data-search]');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape to close modals/panels
        if (e.key === 'Escape') {
            const panels = document.querySelectorAll('.modal, .dropdown[data-open="true"]');
            panels.forEach(panel => {
                panel.classList.add('hidden');
            });
        }
    });

    // Handle form auto-save for wizard
    const wizardForm = document.getElementById('tuning-form');
    if (wizardForm) {
        const inputs = wizardForm.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                const formData = new FormData(wizardForm);
                const data = Object.fromEntries(formData.entries());
                ArrowTuning.storage.set('wizard_form_data', data);
            });
        });

        // Restore form data
        const savedData = ArrowTuning.storage.get('wizard_form_data');
        if (savedData) {
            Object.entries(savedData).forEach(([key, value]) => {
                const input = wizardForm.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = value === 'on';
                    } else {
                        input.value = value;
                    }
                }
            });
        }
    }

    // Initialize tooltips (if using a tooltip library)
    if (typeof tippy !== 'undefined') {
        tippy('[data-tooltip]', {
            content: (reference) => reference.getAttribute('data-tooltip'),
            placement: 'top'
        });
    }
});

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            }, function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export for global use
window.ArrowTuning = ArrowTuning;
window.Comparison = Comparison;
window.Search = Search;