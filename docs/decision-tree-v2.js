// Decision Tree V3 - Sizing-First + Architecture-First + Deselectable Options
//==============================================================================

// State Management (V3: Separated sizing, foundational, and constraint answers)
const state = {
    data: null,
    vendors: null,
    sizingConstraints: {},      // S1-S5: data_volume_gb, growth_rate, source_count, retention_days, budget_k
    foundationalAnswers: {},    // F0-F3: isolation_pattern, table_format, catalog, transformation
    queryEngineCharacteristics: [],  // F4: Multi-select query engine needs
    constraintAnswers: {},      // Q1, Q4: team_size, vendor_tolerance
    cloudEnvironments: [],      // Q3: Multi-select cloud environments
    useCases: [],               // Q5: Multi-select use cases
    vendorCount: 82,
    previousVendorCount: 82,
    filteredVendors: [],
    // Track vendor count at each question for progressive display
    vendorCountsByQuestion: {}
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadDecisionData();
    await loadVendorDatabase();
    renderAllQuestions();
    attachEventListeners();
    updateRecommendations(); // Initial state
});

// Load decision data from JSON (V3: decision-data-v3.json)
async function loadDecisionData() {
    try {
        const response = await fetch('decision-data-v3.json');
        state.data = await response.json();
    } catch (error) {
        console.error('Error loading decision data:', error);
        alert('Failed to load decision tree data. Please refresh the page.');
    }
}

// Load vendor database from JSON
async function loadVendorDatabase() {
    try {
        const response = await fetch('vendor_database.json');
        const data = await response.json();
        state.vendors = data.vendors;
        state.vendorCount = state.vendors.length;
        state.previousVendorCount = state.vendors.length;
    } catch (error) {
        console.error('Error loading vendor database:', error);
        alert('Failed to load vendor database. Please refresh the page.');
    }
}

// Render all questions at once (single page view) - V3: Support slider type
function renderAllQuestions() {
    const container = document.getElementById('questionsContainer');

    const questionsHTML = state.data.questions.map(question => {
        if (question.type === 'slider') {
            return renderSliderQuestion(question);
        } else if (question.type === 'multi_choice') {
            return renderMultiChoiceQuestion(question);
        } else {
            return renderSingleChoiceQuestion(question);
        }
    }).join('');

    container.innerHTML = questionsHTML;
}

// Render single-choice question (radio buttons)
function renderSingleChoiceQuestion(question) {
    return `
        <div class="question-group" data-question-id="${question.id}">
            ${question.section ? `<div class="section-label">${question.section}</div>` : ''}
            <div class="question-title">
                ${question.order}. ${question.title}
                ${question.required ? '<span style="color: #ef4444;">*</span>' : ''}
            </div>
            <div class="question-description">${question.description}</div>
            ${question.help ? `<div class="question-help">💡 ${question.help}</div>` : ''}
            <div class="question-vendor-count" id="count-${question.id}">
                <span class="vendor-count-number" id="count-num-${question.id}">82</span> vendors match
            </div>

            <div class="options">
                ${question.options.map(option => `
                    <label class="option" data-option-id="${option.id}">
                        <input type="radio"
                               name="${question.id}"
                               value="${option.id}"
                               ${!question.required ? '' : 'required'}>
                        <span class="option-label">${option.label}</span>
                        <span class="option-description">${option.description}</span>
                    </label>
                `).join('')}
            </div>
        </div>
    `;
}

// Render multi-choice question (checkboxes)
function renderMultiChoiceQuestion(question) {
    return `
        <div class="question-group" data-question-id="${question.id}">
            ${question.section ? `<div class="section-label">${question.section}</div>` : ''}
            <div class="question-title">
                ${question.order}. ${question.title}
                ${question.required ? '<span style="color: #ef4444;">*</span>' : ''}
            </div>
            <div class="question-description">${question.description}</div>
            ${question.help ? `<div class="question-help">💡 ${question.help}</div>` : ''}
            <div class="question-vendor-count" id="count-${question.id}">
                <span class="vendor-count-number" id="count-num-${question.id}">82</span> vendors match
            </div>

            <div class="options">
                ${question.options.map(option => `
                    <label class="option" data-option-id="${option.id}">
                        <input type="checkbox"
                               name="${question.id}"
                               value="${option.id}">
                        <span class="option-label">${option.label}</span>
                        <span class="option-description">${option.description}</span>
                    </label>
                `).join('')}
            </div>
        </div>
    `;
}

// Render slider question (NEW - V3: For S1-S4 sizing constraints)
function renderSliderQuestion(question) {
    const defaultValue = question.default || question.min;
    const isLogarithmic = question.scale === 'logarithmic';

    return `
        <div class="question-group slider-question" data-question-id="${question.id}">
            ${question.section ? `<div class="section-label">${question.section}</div>` : ''}
            <div class="question-title">
                ${question.order}. ${question.title}
                ${question.required ? '<span style="color: #ef4444;">*</span>' : ''}
            </div>
            <div class="question-description">${question.description}</div>
            ${question.help ? `<div class="question-help">💡 ${question.help}</div>` : ''}
            <div class="question-vendor-count" id="count-${question.id}">
                <span class="vendor-count-number" id="count-num-${question.id}">82</span> vendors match
            </div>

            <div class="slider-container">
                <div class="slider-value-display" id="${question.id}_display">
                    <span class="slider-current-value" id="${question.id}_value">${defaultValue}</span>
                    <span class="slider-unit">${question.unit}</span>
                </div>

                <input type="range"
                       id="${question.id}_slider"
                       name="${question.id}"
                       min="${isLogarithmic ? 0 : question.min}"
                       max="${isLogarithmic ? (question.markers.length - 1) : question.max}"
                       value="${isLogarithmic ? 2 : defaultValue}"
                       step="${isLogarithmic ? 1 : (question.max - question.min) / 100}"
                       class="slider"
                       data-scale="${question.scale}"
                       data-markers='${JSON.stringify(question.markers)}'>

                <div class="slider-markers">
                    ${question.markers.map((marker, idx) => {
                        const value = typeof marker === 'object' ? marker.value : marker;
                        const label = typeof marker === 'object' ? marker.label : formatSliderLabel(value, question.unit);
                        return `<span class="slider-marker" data-index="${idx}">${label}</span>`;
                    }).join('')}
                </div>
            </div>
        </div>
    `;
}

// Format slider label for display
function formatSliderLabel(value, unit) {
    if (unit === 'GB/day') {
        if (value >= 1000) return `${value/1000} TB/day`;
        return `${value} GB/day`;
    } else if (unit === '$K/year') {
        if (value >= 1000) return `$${value/1000}M/year`;
        return `$${value}K/year`;
    } else if (unit === 'days') {
        if (value >= 365) {
            const years = Math.floor(value / 365);
            return years === 1 ? '1 year' : `${years} years`;
        }
        return `${value} days`;
    }
    return value + (unit ? ' ' + unit : '');
}

// Attach event listeners to all inputs (V3: sliders + deselectable radios)
function attachEventListeners() {
    // Sliders (NEW - V3)
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        slider.addEventListener('input', handleSliderChange);
    });

    // Radio buttons with DESELECTION support (click, not change)
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('click', handleRadioClick);
    });

    // Checkboxes (multi-select)
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleCheckboxChange);
    });

    // Buttons
    document.getElementById('downloadBtn').addEventListener('click', downloadReport);
    document.getElementById('resetBtn').addEventListener('click', resetForm);

    // Modal functionality
    setupVendorModal();
}

// Handle slider change (NEW - V3: For S1-S4 sizing constraints)
function handleSliderChange(event) {
    const questionId = event.target.name;
    const slider = event.target;
    const isLogarithmic = slider.dataset.scale === 'logarithmic';
    const markers = JSON.parse(slider.dataset.markers);

    let actualValue;
    if (isLogarithmic) {
        // Convert slider index to actual value from markers
        const index = parseInt(slider.value);
        actualValue = typeof markers[index] === 'object' ? markers[index].value : markers[index];
    } else {
        actualValue = parseFloat(slider.value);
    }

    // Store in sizing constraints
    state.sizingConstraints[questionId] = actualValue;

    // Update display
    const question = state.data.questions.find(q => q.id === questionId);
    const valueDisplay = document.getElementById(`${questionId}_value`);
    valueDisplay.textContent = formatSliderLabel(actualValue, question.unit);

    // Update recommendations in real-time
    updateRecommendations();
}

// Handle radio button click with DESELECTION support (NEW - V3)
function handleRadioClick(event) {
    const questionId = event.target.name;
    const optionId = event.target.value;
    const radio = event.target;

    // Check if this radio is already selected
    const wasSelected = radio.classList.contains('was-selected');

    if (wasSelected) {
        // Deselect: uncheck radio and remove answer
        radio.checked = false;
        radio.classList.remove('was-selected');

        // Remove from appropriate state storage
        if (questionId.startsWith('f')) {
            delete state.foundationalAnswers[questionId];
        } else if (questionId.startsWith('q')) {
            delete state.constraintAnswers[questionId];
        }

        // Remove visual feedback
        const questionGroup = document.querySelector(`[data-question-id="${questionId}"]`);
        questionGroup.querySelectorAll('.option').forEach(opt => {
            opt.classList.remove('selected');
        });
    } else {
        // Select: store answer and update visual feedback
        // Store answer in appropriate bucket
        if (questionId.startsWith('s')) {
            state.sizingConstraints[questionId] = optionId;
        } else if (questionId.startsWith('f')) {
            state.foundationalAnswers[questionId] = optionId;
        } else if (questionId.startsWith('q')) {
            state.constraintAnswers[questionId] = optionId;
        }

        // Visual feedback
        const questionGroup = document.querySelector(`[data-question-id="${questionId}"]`);
        questionGroup.querySelectorAll('.option').forEach(opt => {
            opt.classList.remove('selected');
        });
        questionGroup.querySelectorAll('input[type="radio"]').forEach(r => {
            r.classList.remove('was-selected');
        });
        event.target.closest('.option').classList.add('selected');
        radio.classList.add('was-selected');
    }

    // Update recommendations in real-time
    updateRecommendations();
}

// Handle checkbox change (multi-select for F4, Q3, Q5) - V3: Support multiple multi-selects
function handleCheckboxChange(event) {
    const questionId = event.target.name;
    const optionId = event.target.value;

    // Determine which array to update
    let targetArray;
    if (questionId === 'f4_query_engine') {
        targetArray = state.queryEngineCharacteristics;
    } else if (questionId === 'q3_cloud_environment') {
        targetArray = state.cloudEnvironments;
    } else if (questionId === 'q5_use_cases') {
        targetArray = state.useCases;
    }

    if (targetArray) {
        if (event.target.checked) {
            targetArray.push(optionId);
        } else {
            // Remove from array
            const index = targetArray.indexOf(optionId);
            if (index > -1) {
                targetArray.splice(index, 1);
            }
        }

        // Visual feedback
        if (event.target.checked) {
            event.target.closest('.option').classList.add('selected');
        } else {
            event.target.closest('.option').classList.remove('selected');
        }
    }

    // Update recommendations in real-time
    updateRecommendations();
}

// Update recommendations based on current answers (V3: Updated for new state structure)
function updateRecommendations() {
    // Filter vendors based on sizing → architecture → constraints
    filterVendors();

    // Get isolation pattern from F0 (no longer derived)
    const isolationPattern = state.foundationalAnswers.f0_isolation_pattern;

    // Update recommendation sections
    updateArchitectureStack(isolationPattern);
    updatePerformanceTCO(isolationPattern);
    updateProductionExamples(isolationPattern);
    updateVendorRecommendations();

    // Enable download button if all required questions answered
    updateDownloadButton();
}

// VENDOR FILTERING LOGIC - V3: Sizing → Architecture → Constraints
function filterVendors() {
    let filtered = [...state.vendors];
    const sizing = state.sizingConstraints;
    const foundational = state.foundationalAnswers;
    const constraints = state.constraintAnswers;

    // Initialize scores
    filtered.forEach(v => { v.score = 0; });

    // ========================================================================
    // PHASE 0: SIZING CONSTRAINTS (S1-S4) - Filter by data volume and scale
    // ========================================================================

    // S1: Data volume (GB/day) - Eliminates vendors by scale
    const dataVolumeGB = sizing.s1_data_volume;
    if (dataVolumeGB) {
        if (dataVolumeGB < 10) {
            // 0-10 GB/day: Eliminate Splunk (overkill, $100K+ minimum)
            filtered = filtered.filter(v =>
                !v.id.includes('splunk')
            );
        } else if (dataVolumeGB >= 100 && dataVolumeGB < 1000) {
            // 100 GB-1 TB/day: Eliminate DuckDB (single-process max ~500 GB/day)
            filtered = filtered.filter(v => v.id !== 'duckdb');
        } else if (dataVolumeGB >= 1000) {
            // 1+ TB/day: Eliminate DuckDB and small-scale vendors
            filtered = filtered.filter(v =>
                v.id !== 'duckdb' &&
                v.capabilities.deployment_models &&
                (v.capabilities.deployment_models.includes('cloud') ||
                 v.capabilities.deployment_models.includes('hybrid'))
            );
        }
    }

    // S2: Growth rate (%) - Favor elastic/serverless for high growth
    const growthRate = sizing.s2_growth_rate;
    if (growthRate && growthRate >= 100) {
        // 100%+ growth: Boost serverless/elastic architectures
        filtered.forEach(v => {
            if (v.capabilities.cloud_native || v.id.includes('athena') || v.id.includes('databricks')) {
                v.score += 2;
            }
        });
    }

    // S3: Source count - Suggest ETL layer for 100+ sources
    const sourceCount = sizing.s3_source_count;
    if (sourceCount && sourceCount >= 100) {
        // 100+ sources: Boost ETL/normalization vendors
        filtered.forEach(v => {
            if (v.id.includes('cribl') || v.id.includes('tenzir') || v.category === 'ETL/ELT') {
                v.score += 2;
            }
        });
    }

    // S4: Retention (days) - Require tiering for 2+ years
    const retentionDays = sizing.s4_retention;
    if (retentionDays && retentionDays >= 730) {
        // 2+ years retention: Boost vendors with hot/warm/cold tiering
        filtered.forEach(v => {
            if (v.capabilities.iceberg_support) {
                v.score += 1;  // Iceberg time-travel beneficial for long retention
            }
        });
    }

    // ========================================================================
    // PHASE 1: FOUNDATIONAL ARCHITECTURE (F0-F4) - Establish architecture
    // ========================================================================

    // F0: Isolation pattern (THE most important architectural decision)
    const isolationPattern = foundational.f0_isolation_pattern;
    if (isolationPattern === 'shared_corporate' || isolationPattern === 'multi_tenant_mssp') {
        // Shared platforms REQUIRE Unity Catalog for RLS
        filtered = filtered.filter(v =>
            v.capabilities.unity_catalog_support === true ||
            v.id === 'unity-catalog' ||
            v.id === 'databricks'
        );
    } else if (isolationPattern === 'isolated_dedicated') {
        // Isolated platforms prefer Polaris/Nessie (OSS, 0% RLS overhead)
        filtered = filtered.filter(v =>
            v.capabilities.polaris_catalog_support === true ||
            v.capabilities.nessie_catalog_support === true ||
            v.capabilities.iceberg_support === true ||
            v.id === 'polaris' ||
            v.id === 'nessie'
        );
    }

    // F1: Table format (multi-year commitment)
    const tableFormat = foundational.f1_table_format;
    if (tableFormat === 'iceberg') {
        filtered = filtered.filter(v => v.capabilities.iceberg_support === true);
    } else if (tableFormat === 'delta_lake') {
        filtered = filtered.filter(v => v.capabilities.delta_lake_support === true);
    } else if (tableFormat === 'hudi') {
        filtered = filtered.filter(v => v.capabilities.hudi_support === true);
    } else if (tableFormat === 'proprietary') {
        filtered = filtered.filter(v =>
            v.id.includes('snowflake') ||
            v.capabilities.proprietary_format === true
        );
    }

    // F2: Catalog (governance requirements)
    const catalog = foundational.f2_catalog;
    if (catalog === 'polaris') {
        filtered = filtered.filter(v =>
            v.capabilities.polaris_catalog_support === true ||
            v.id === 'polaris'
        );
    } else if (catalog === 'unity_catalog') {
        filtered = filtered.filter(v =>
            v.capabilities.unity_catalog_support === true ||
            v.id === 'unity-catalog'
        );
    } else if (catalog === 'nessie') {
        filtered = filtered.filter(v =>
            v.capabilities.nessie_catalog_support === true ||
            v.id === 'nessie'
        );
    } else if (catalog === 'glue') {
        filtered = filtered.filter(v =>
            v.capabilities.glue_catalog_support === true ||
            v.id.includes('glue')
        );
    }

    // F3: Transformation strategy
    const transformation = foundational.f3_transformation;
    if (transformation === 'dbt') {
        filtered = filtered.filter(v => v.capabilities.dbt_integration === true);
    } else if (transformation === 'vendor_builtin') {
        filtered = filtered.filter(v =>
            v.id.includes('splunk') ||
            v.id.includes('sentinel') ||
            v.id.includes('elastic')
        );
    }

    // F4: Query engine characteristics (MULTI-SELECT - can select multiple needs)
    if (state.queryEngineCharacteristics.length > 0) {
        // Score vendors based on how many query engine needs they meet
        filtered.forEach(v => {
            if (state.queryEngineCharacteristics.includes('low_latency')) {
                if (v.id.includes('clickhouse') || v.id.includes('pinot') ||
                    (v.capabilities.query_latency_p95 && v.capabilities.query_latency_p95 < 1000)) {
                    v.score += 3;
                }
            }
            if (state.queryEngineCharacteristics.includes('high_concurrency')) {
                if (v.id.includes('trino') || v.id.includes('presto') ||
                    v.id.includes('dremio') || v.id.includes('starburst')) {
                    v.score += 2;
                }
            }
            if (state.queryEngineCharacteristics.includes('serverless')) {
                if (v.id.includes('athena') || v.id.includes('snowflake') ||
                    v.id.includes('databricks') || v.capabilities.serverless === true) {
                    v.score += 2;
                }
            }
            if (state.queryEngineCharacteristics.includes('cost_optimized')) {
                if (v.id === 'duckdb') {
                    v.score += 3;
                }
            }
        });
    }

    // ========================================================================
    // PHASE 2: ORGANIZATIONAL CONSTRAINTS (Q1-Q4) - Filter within architecture
    // ========================================================================

    // Q1: Team size
    const teamSize = constraints.q1_team_size;
    if (teamSize === 'lean') {
        // Lean teams need low operational complexity OR managed services
        filtered = filtered.filter(v =>
            v.capabilities.operational_complexity === 'low' ||
            v.capabilities.managed_service_available === true
        );
    }

    // Q2: Budget (SLIDER - stored in sizing constraints)
    const budgetK = sizing.q2_budget;  // Budget in $K/year
    if (budgetK && budgetK < 500) {
        // <$500K: Eliminate Unity Catalog, Databricks, Snowflake, Splunk
        filtered = filtered.filter(v => {
            const costRange = v.typical_annual_cost_range.toLowerCase();
            return !costRange.includes('$1m') &&
                   !costRange.includes('$2m') &&
                   !v.id.includes('databricks') &&
                   !v.id.includes('snowflake') &&
                   !v.id.includes('splunk');
        });
    }

    // Q3: Cloud environment (MULTI-SELECT - can select multiple clouds)
    if (state.cloudEnvironments.length > 0) {
        // If on-prem is selected, require on-prem or hybrid support
        if (state.cloudEnvironments.includes('on_prem')) {
            filtered = filtered.filter(v =>
                v.capabilities.deployment_models &&
                (v.capabilities.deployment_models.includes('on-prem') ||
                 v.capabilities.deployment_models.includes('hybrid'))
            );
        }

        // If multiple clouds selected (excluding multi_cloud option), boost cloud-agnostic vendors
        const cloudProviders = state.cloudEnvironments.filter(env =>
            env === 'aws' || env === 'azure' || env === 'gcp'
        );
        if (cloudProviders.length > 1) {
            // Multi-cloud scenario: boost cloud-agnostic vendors
            filtered.forEach(v => {
                if (v.capabilities.multi_cloud === true) {
                    v.score += 2;
                }
            });
        } else if (cloudProviders.length === 1) {
            // Single cloud: boost cloud-native vendors
            const cloud = cloudProviders[0];
            filtered.forEach(v => {
                if (cloud === 'aws' && v.id.includes('aws')) v.score += 1;
                if (cloud === 'azure' && v.id.includes('azure')) v.score += 1;
                if (cloud === 'gcp' && v.id.includes('gcp')) v.score += 1;
            });
        }
    }

    // Q4: Vendor tolerance
    const vendorTolerance = constraints.q4_vendor_tolerance;
    if (vendorTolerance === 'oss_first') {
        filtered = filtered.filter(v =>
            v.vendor_type === 'open_source' ||
            v.cost_notes.toLowerCase().includes('oss') ||
            v.cost_notes.toLowerCase().includes('open source')
        );
    } else if (vendorTolerance === 'commercial_only') {
        filtered = filtered.filter(v => v.vendor_type !== 'open_source');
    }

    // ========================================================================
    // PHASE 3: USE CASES (Q5) - Score vendors on use case fit
    // ========================================================================

    if (state.useCases.includes('real_time_dashboards')) {
        filtered.forEach(v => {
            if (v.capabilities.query_latency_p95 && v.capabilities.query_latency_p95 < 1000) {
                v.score += 3;  // Boost for low latency
            }
        });
    }

    if (state.useCases.includes('ad_hoc_hunting')) {
        filtered.forEach(v => {
            if (v.id === 'duckdb' || v.id.includes('trino')) {
                v.score += 2;
            }
        });
    }

    if (state.useCases.includes('compliance_reporting')) {
        filtered.forEach(v => {
            if (v.id.includes('athena') || v.capabilities.serverless) {
                v.score += 2;
            }
        });
    }

    if (state.useCases.includes('detection_rules')) {
        filtered.forEach(v => {
            if (v.id.includes('kafka') || v.id.includes('flink') || v.id.includes('cribl')) {
                v.score += 3;
            }
        });
    }

    // Sort by score (highest first)
    filtered.sort((a, b) => (b.score || 0) - (a.score || 0));

    // Update state
    state.filteredVendors = filtered;
    state.previousVendorCount = state.vendorCount;
    state.vendorCount = filtered.length;

    // Update vendor count UI
    document.getElementById('vendorCount').textContent = state.vendorCount;

    const changeEl = document.getElementById('vendorChange');
    const change = state.vendorCount - state.previousVendorCount;
    if (change < 0) {
        changeEl.textContent = `${change} from filters applied`;
        changeEl.className = 'metric-change negative';
    } else if (change > 0) {
        changeEl.textContent = `+${change} from filters removed`;
        changeEl.className = 'metric-change';
    } else {
        changeEl.textContent = '';
    }

    // Update per-question vendor counts
    updateQuestionVendorCounts();
}

// Update vendor count display for each question
function updateQuestionVendorCounts() {
    // For each question, simulate filtering to determine vendor count at that step
    const questions = state.data.questions;

    questions.forEach(question => {
        const countElement = document.getElementById(`count-num-${question.id}`);
        if (!countElement) return;

        // Get the current vendor count for this question from state
        const count = state.vendorCountsByQuestion[question.id] || state.vendorCount;
        countElement.textContent = count;

        // Color coding based on filter impact
        const countContainer = document.getElementById(`count-${question.id}`);
        if (countContainer) {
            const previousCount = state.vendorCountsByQuestion[`${question.id}_previous`] || 82;
            const reduction = previousCount - count;

            if (reduction === 0) {
                countContainer.className = 'question-vendor-count no-change';
            } else if (reduction > 0 && reduction < 20) {
                countContainer.className = 'question-vendor-count moderate-reduction';
            } else if (reduction >= 20) {
                countContainer.className = 'question-vendor-count high-reduction';
            }
        }
    });
}

// Display top 3-5 vendor recommendations
function updateVendorRecommendations() {
    // Add vendor list section to recommendations panel if it doesn't exist
    let vendorSection = document.getElementById('vendorRecommendations');
    if (!vendorSection) {
        const performanceSection = document.getElementById('performanceTCO');
        vendorSection = document.createElement('div');
        vendorSection.id = 'vendorRecommendations';
        vendorSection.className = 'recommendation-section';
        performanceSection.after(vendorSection);
    }

    const topVendors = state.filteredVendors.slice(0, 5);  // Top 5

    if (topVendors.length === 0) {
        vendorSection.innerHTML = `
            <h3>🏢 Top Vendor Matches</h3>
            <p style="color: #6b7280; font-size: 0.9rem;">Answer all questions to see vendor recommendations</p>
        `;
        return;
    }

    vendorSection.innerHTML = `
        <h3>🏢 Top ${topVendors.length} Vendor Matches</h3>
        ${topVendors.map((vendor, idx) => `
            <div class="vendor-card">
                <div class="vendor-header">
                    <span class="vendor-rank">${idx + 1}</span>
                    <div>
                        <div class="vendor-name">${vendor.name}</div>
                        <div class="vendor-category">${vendor.category}</div>
                    </div>
                </div>
                <div class="vendor-description">${vendor.description.substring(0, 150)}...</div>
                <div class="vendor-meta">
                    <span class="vendor-cost">💰 ${vendor.typical_annual_cost_range}</span>
                    ${vendor.capabilities.managed_service_available ? '<span class="vendor-badge">Managed Service</span>' : ''}
                    ${vendor.capabilities.cloud_native ? '<span class="vendor-badge">Cloud Native</span>' : ''}
                </div>
                <a href="${vendor.website}" target="_blank" class="vendor-link">Learn More →</a>
            </div>
        `).join('')}
    `;
}

// Update architecture stack recommendations (V3: Use new state structure)
function updateArchitectureStack(isolationPattern) {
    const foundational = state.foundationalAnswers;
    const constraints = state.constraintAnswers;

    // Isolation Pattern (F0)
    if (isolationPattern) {
        const patterns = {
            'isolated_dedicated': 'Isolated Dedicated (0% RLS overhead)',
            'shared_corporate': 'Shared Corporate (15-50% RLS overhead)',
            'multi_tenant_mssp': 'Multi-tenant MSSP (5-30% RLS overhead)'
        };
        document.getElementById('isolationPattern').textContent = patterns[isolationPattern] || 'Not determined';
    } else {
        document.getElementById('isolationPattern').textContent = 'Answer F0 to determine';
    }

    // Catalog Recommendation (F2 or derived from F0+Q2)
    const budgetK = state.sizingConstraints.q2_budget;
    let catalogRec = foundational.f2_catalog || 'Answer F0 & F2';
    if (!foundational.f2_catalog && budgetK && isolationPattern) {
        // Derive recommendation if not explicitly selected
        if (budgetK < 500 && isolationPattern === 'isolated_dedicated') {
            catalogRec = 'Polaris or Nessie (OSS, $0)';
        } else if (isolationPattern === 'shared_corporate' || isolationPattern === 'multi_tenant_mssp') {
            catalogRec = 'Unity Catalog (REQUIRED for RLS)';
        } else if (isolationPattern === 'isolated_dedicated') {
            catalogRec = 'Polaris (vendor-neutral) or Nessie (Git workflows)';
        }
    } else if (foundational.f2_catalog) {
        const catalogs = {
            'polaris': 'Polaris (Iceberg-native, OSS)',
            'unity_catalog': 'Unity Catalog (Delta-native, RLS)',
            'nessie': 'Nessie (Git-like, OSS)',
            'glue': 'AWS Glue (Serverless)',
            'hive_metastore': 'Hive Metastore (Legacy)'
        };
        catalogRec = catalogs[foundational.f2_catalog] || foundational.f2_catalog;
    }
    document.getElementById('catalogRec').textContent = catalogRec;

    // Table Format Recommendation (F1)
    let tableFormatRec = foundational.f1_table_format || 'Answer F1';
    if (foundational.f1_table_format) {
        const formats = {
            'iceberg': 'Apache Iceberg',
            'delta_lake': 'Delta Lake',
            'hudi': 'Apache Hudi',
            'proprietary': 'Proprietary (Snowflake)',
            'undecided': isolationPattern === 'isolated_dedicated' ? 'Iceberg (recommended)' : 'Delta Lake or Iceberg'
        };
        tableFormatRec = formats[foundational.f1_table_format] || foundational.f1_table_format;
    } else if (isolationPattern) {
        tableFormatRec = isolationPattern === 'isolated_dedicated' ? 'Iceberg (recommended)' : 'Delta Lake or Iceberg';
    }
    document.getElementById('tableFormatRec').textContent = tableFormatRec;

    // Query Engine Recommendation (F4 MULTI-SELECT or derived from Q5 use cases)
    let queryEngineRec = 'Answer F4 or Q5';
    if (state.queryEngineCharacteristics.length > 0) {
        const engines = [];
        if (state.queryEngineCharacteristics.includes('low_latency')) engines.push('ClickHouse');
        if (state.queryEngineCharacteristics.includes('high_concurrency')) engines.push('Trino');
        if (state.queryEngineCharacteristics.includes('serverless')) engines.push('Athena');
        if (state.queryEngineCharacteristics.includes('cost_optimized')) engines.push('DuckDB');
        if (state.queryEngineCharacteristics.includes('flexible')) engines.push('Trino');
        queryEngineRec = engines.length > 0 ? engines.join(' + ') : 'Trino (flexible)';
    } else if (state.useCases.length > 0) {
        // Derive from use cases
        const engines = [];
        if (state.useCases.includes('real_time_dashboards')) engines.push('ClickHouse');
        if (state.useCases.includes('ad_hoc_hunting')) engines.push('DuckDB');
        if (state.useCases.includes('compliance_reporting')) engines.push('Athena');
        if (state.useCases.includes('detection_rules')) engines.push('Kafka + Flink');
        queryEngineRec = engines.length > 0 ? engines.join(' + ') : 'Trino (flexible)';
    }
    document.getElementById('queryEngineRec').textContent = queryEngineRec;
}

// Update performance and TCO metrics (V3: Use new state structure)
function updatePerformanceTCO(isolationPattern) {
    const budgetK = state.sizingConstraints.q2_budget;
    const container = document.getElementById('performanceMetrics');

    if (!isolationPattern || !budgetK) {
        container.innerHTML = '<p style="color: #6b7280; font-size: 0.9rem;">Answer F0 & Q2 for performance/cost estimates</p>';
        return;
    }

    // Get isolation pattern details from F0 question
    const question = state.data.questions.find(q => q.id === 'f0_isolation_pattern');
    const option = question ? question.options.find(opt => opt.id === isolationPattern) : null;

    let performanceHTML = '';

    if (option) {
        if (option.performance_gain) {
            performanceHTML += `<div class="performance-badge good">⚡ ${option.performance_gain}</div>`;
        } else if (option.performance_overhead) {
            const badgeClass = option.performance_overhead.includes('15-50') ? 'high' : 'moderate';
            performanceHTML += `<div class="performance-badge ${badgeClass}">⚠️ ${option.performance_overhead}</div>`;
        }

        performanceHTML += `<div class="performance-badge ${option.tco.includes('Low') ? 'good' : 'high'}">💰 TCO: ${option.tco}</div>`;
    }

    container.innerHTML = performanceHTML;
}

// Update production examples (V3: Use new state structure)
function updateProductionExamples(isolationPattern) {
    const container = document.getElementById('productionExamples');
    const list = document.getElementById('examplesList');

    if (!isolationPattern) {
        container.style.display = 'none';
        return;
    }

    // Get isolation pattern details from F0 question
    const question = state.data.questions.find(q => q.id === 'f0_isolation_pattern');
    const option = question ? question.options.find(opt => opt.id === isolationPattern) : null;

    if (option && option.production_examples) {
        container.style.display = 'block';
        list.innerHTML = option.production_examples.map(ex => `<li>${ex}</li>`).join('');
    } else {
        container.style.display = 'none';
    }
}

// Update download button state (V3: Check all state buckets including multi-selects)
function updateDownloadButton() {
    const requiredQuestions = state.data.questions.filter(q => q.required).map(q => q.id);
    const allAnswered = requiredQuestions.every(qId => {
        // Multi-select questions
        if (qId === 'q5_use_cases') {
            return state.useCases.length > 0;
        }
        if (qId === 'f4_query_engine') {
            return state.queryEngineCharacteristics.length > 0;
        }
        if (qId === 'q3_cloud_environment') {
            return state.cloudEnvironments.length > 0;
        }

        // Check appropriate state bucket for single-select and sliders
        if (qId.startsWith('s') || qId === 'q2_budget') {
            return state.sizingConstraints[qId] !== undefined;
        } else if (qId.startsWith('f')) {
            return state.foundationalAnswers[qId] !== undefined;
        } else if (qId.startsWith('q')) {
            return state.constraintAnswers[qId] !== undefined;
        }
        return false;
    });

    document.getElementById('downloadBtn').disabled = !allAnswered;
}

// Download report WITH ACTUAL VENDORS
function downloadReport() {
    const reportContent = generateTextReport();
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `security-architecture-decision-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Generate text report WITH VENDOR RECOMMENDATIONS (V3: Use new state structure)
function generateTextReport() {
    const isolationPattern = state.foundationalAnswers.f0_isolation_pattern;
    const topVendors = state.filteredVendors.slice(0, 5);

    return `
SECURITY DATA PLATFORM ARCHITECTURE RECOMMENDATION REPORT
==========================================================

Generated: ${new Date().toLocaleString()}
Tool: Security Data Platform Architecture Decision Tool (v3.0)
Source: Modern Data Stack for Cybersecurity by Jeremy Wiley

SIZING CONSTRAINTS
------------------

Data Volume: ${state.sizingConstraints.s1_data_volume ? formatSliderLabel(state.sizingConstraints.s1_data_volume, 'GB/day') : 'Not specified'}
Growth Rate: ${state.sizingConstraints.s2_growth_rate ? state.sizingConstraints.s2_growth_rate + '% annually' : 'Not specified'}
Source Count: ${state.sizingConstraints.s3_source_count ? state.sizingConstraints.s3_source_count + ' sources' : 'Not specified'}
Retention: ${state.sizingConstraints.s4_retention ? state.sizingConstraints.s4_retention + ' days' : 'Not specified'}

FOUNDATIONAL ARCHITECTURE
--------------------------

Isolation Pattern: ${getAnswerLabel('f0_isolation_pattern')}
Table Format: ${getAnswerLabel('f1_table_format')}
Catalog: ${getAnswerLabel('f2_catalog')}
Transformation: ${getAnswerLabel('f3_transformation')}
Query Engine: ${getAnswerLabel('f4_query_engine')}

ORGANIZATIONAL CONSTRAINTS
---------------------------

Team Capacity: ${getAnswerLabel('q1_team_size')}
Budget: ${getAnswerLabel('q2_budget')}
Cloud Environment: ${getAnswerLabel('q3_cloud_environment')}
Vendor Tolerance: ${getAnswerLabel('q4_vendor_tolerance')}

USE CASES
---------

Primary Use Cases: ${state.useCases.map(id => getUseCaseLabel(id)).join(', ')}

RECOMMENDED ARCHITECTURE STACK
-------------------------------

Isolation Pattern: ${isolationPattern || 'Not determined'}
Catalog: ${document.getElementById('catalogRec').textContent}
Table Format: ${document.getElementById('tableFormatRec').textContent}
Query Engine: ${document.getElementById('queryEngineRec').textContent}

TOP ${topVendors.length} VENDOR RECOMMENDATIONS
${'-'.repeat(50)}

${topVendors.map((vendor, idx) => `
${idx + 1}. ${vendor.name} (${vendor.category})
   ${'-'.repeat(60)}
   Description: ${vendor.description}

   Cost Range: ${vendor.typical_annual_cost_range}
   ${vendor.cost_notes}

   Key Capabilities:
   ${vendor.capabilities.managed_service_available ? '✓ Managed service available' : ''}
   ${vendor.capabilities.cloud_native ? '✓ Cloud-native architecture' : ''}
   ${vendor.capabilities.iceberg_support ? '✓ Iceberg support' : ''}
   ${vendor.capabilities.unity_catalog_support ? '✓ Unity Catalog support' : ''}
   ${vendor.capabilities.dbt_integration ? '✓ dbt integration' : ''}

   Operational Complexity: ${vendor.capabilities.operational_complexity}
   Team Size Required: ${vendor.capabilities.team_size_required}

   Learn More: ${vendor.website}

`).join('\n')}

${isolationPattern ? `
PERFORMANCE & COST IMPACT
--------------------------

${document.getElementById('performanceMetrics').textContent}

PRODUCTION VALIDATION
---------------------

This architecture pattern is validated by:
${document.getElementById('examplesList').innerHTML.replace(/<li>/g, '• ').replace(/<\/li>/g, '\n')}
` : ''}

NEXT STEPS
----------

1. Review detailed vendor analysis for top ${topVendors.length} matches above
2. Request demos from top 3 vendors
3. Calculate detailed TCO for each finalist (5-year projections)
4. Conduct proof-of-concept testing with realistic security data
5. Read detailed blog posts: https://securitydatacommons.substack.com

DISCLAIMERS
-----------

• No vendor sponsorships - all recommendations evidence-based
• Validate cost estimates with vendors directly (ranges may vary by scale)
• Test architecture patterns before production deployment
• Consult security/compliance teams for regulatory requirements
• Vendor database updated: ${new Date().toLocaleDateString()}

Report generated by Security Data Platform Architecture Decision Tool
https://flying-coyote.github.io/security-architect-mcp-server/
    `.trim();
}

// Helper: Get answer label from question ID (V3: Check all state buckets + handle sliders/arrays)
function getAnswerLabel(questionId) {
    let answer;
    const question = state.data.questions.find(q => q.id === questionId);
    if (!question) return 'Unknown';

    // Check appropriate state bucket
    if (questionId.startsWith('s') || questionId === 'q2_budget') {
        answer = state.sizingConstraints[questionId];
        // For sliders, format the value with unit
        if (answer !== undefined && question.type === 'slider') {
            return formatSliderLabel(answer, question.unit);
        }
    } else if (questionId === 'f4_query_engine') {
        // F4 is multi-select
        if (state.queryEngineCharacteristics.length === 0) return 'Not answered';
        return state.queryEngineCharacteristics.map(id => {
            const opt = question.options.find(o => o.id === id);
            return opt ? opt.label : id;
        }).join(', ');
    } else if (questionId.startsWith('f')) {
        answer = state.foundationalAnswers[questionId];
    } else if (questionId === 'q3_cloud_environment') {
        // Q3 is multi-select
        if (state.cloudEnvironments.length === 0) return 'Not answered';
        return state.cloudEnvironments.map(id => {
            const opt = question.options.find(o => o.id === id);
            return opt ? opt.label : id;
        }).join(', ');
    } else if (questionId.startsWith('q')) {
        answer = state.constraintAnswers[questionId];
    }

    if (!answer) return 'Not answered';

    const option = question.options.find(opt => opt.id === answer);
    return option ? option.label : answer;
}

// Helper: Get use case label (V3: Updated question ID)
function getUseCaseLabel(useCaseId) {
    const question = state.data.questions.find(q => q.id === 'q5_use_cases');
    if (!question) return useCaseId;

    const option = question.options.find(opt => opt.id === useCaseId);
    return option ? option.label : useCaseId;
}

// Reset form (V3: Clear all new state buckets)
function resetForm() {
    // Clear all answer buckets
    state.sizingConstraints = {};
    state.foundationalAnswers = {};
    state.queryEngineCharacteristics = [];
    state.constraintAnswers = {};
    state.cloudEnvironments = [];
    state.useCases = [];
    state.vendorCount = state.vendors ? state.vendors.length : 82;
    state.previousVendorCount = state.vendorCount;
    state.filteredVendors = state.vendors ? [...state.vendors] : [];

    // Clear all radio/checkbox/slider selections
    document.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(input => {
        input.checked = false;
        input.classList.remove('was-selected');
    });

    // Reset sliders to default values
    document.querySelectorAll('input[type="range"]').forEach(slider => {
        const question = state.data.questions.find(q => q.id === slider.name);
        if (question) {
            const defaultValue = question.default || question.min;
            const isLogarithmic = question.scale === 'logarithmic';
            slider.value = isLogarithmic ? 2 : defaultValue;

            // Update display
            const valueDisplay = document.getElementById(`${slider.name}_value`);
            if (valueDisplay) {
                valueDisplay.textContent = formatSliderLabel(defaultValue, question.unit);
            }
        }
    });

    // Clear all selected visual states
    document.querySelectorAll('.option').forEach(opt => {
        opt.classList.remove('selected');
    });

    // Reset recommendations
    updateRecommendations();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Modal Functionality - Show list of all matching vendors
function setupVendorModal() {
    const modal = document.getElementById('vendorModal');
    const vendorCountCard = document.getElementById('vendorCountCard');
    const closeBtn = document.querySelector('.modal-close');

    // Open modal when vendor count is clicked
    vendorCountCard.addEventListener('click', () => {
        showVendorModal();
    });

    // Close modal when X is clicked
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    // Close modal when clicking outside of it
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });

    // Close modal with ESC key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
        }
    });
}

// Show vendor modal with current filtered vendors
function showVendorModal() {
    const modal = document.getElementById('vendorModal');
    const modalVendorCount = document.getElementById('modalVendorCount');
    const vendorList = document.getElementById('vendorList');
    const filterSummary = document.getElementById('filterSummary');

    // Update vendor count in modal header
    modalVendorCount.textContent = state.vendorCount;

    // Build filter summary text
    const filters = [];
    if (state.sizingConstraints.s1_data_volume) {
        filters.push(`Data volume: ${formatSliderLabel(state.sizingConstraints.s1_data_volume, 'GB/day')}`);
    }
    if (state.sizingConstraints.q2_budget) {
        filters.push(`Budget: ${formatSliderLabel(state.sizingConstraints.q2_budget, '$K/year')}`);
    }
    if (state.foundationalAnswers.f0_isolation_pattern) {
        filters.push(`Isolation: ${getAnswerLabel('f0_isolation_pattern')}`);
    }
    if (state.foundationalAnswers.f1_table_format) {
        filters.push(`Table format: ${getAnswerLabel('f1_table_format')}`);
    }

    filterSummary.textContent = filters.length > 0
        ? `Vendors matching: ${filters.join(', ')}`
        : 'All vendors (no filters applied yet)';

    // Display vendors
    const vendors = state.filteredVendors.length > 0 ? state.filteredVendors : state.vendors;

    if (!vendors || vendors.length === 0) {
        vendorList.innerHTML = `
            <p style="color: #6b7280; text-align: center; padding: 20px;">
                No vendors match your current criteria. Try adjusting your filters.
            </p>
        `;
    } else {
        vendorList.innerHTML = vendors.map(vendor => `
            <div class="vendor-list-item" onclick="window.open('${vendor.website}', '_blank')">
                <div class="vendor-list-item-header">
                    <div class="vendor-list-item-name">${vendor.name}</div>
                    <div class="vendor-list-item-category">${vendor.category}</div>
                </div>
                <div class="vendor-list-item-meta">
                    <span class="vendor-list-item-cost">${vendor.typical_annual_cost_range}</span>
                    ${vendor.score > 0 ? `<span class="vendor-list-item-badge">Score: ${vendor.score}</span>` : ''}
                    ${vendor.capabilities.cloud_native ? '<span class="vendor-list-item-badge">Cloud</span>' : ''}
                    ${vendor.capabilities.managed_service_available ? '<span class="vendor-list-item-badge">Managed</span>' : ''}
                </div>
            </div>
        `).join('');
    }

    // Show modal
    modal.classList.add('active');
}
