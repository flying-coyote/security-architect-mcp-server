// Decision Tree V2 - Single Page with Real-time Updates + ACTUAL VENDOR FILTERING
//==============================================================================

// State Management
const state = {
    data: null,
    vendors: null,
    answers: {},
    useCases: [],  // Multi-select for Q5
    vendorCount: 71,
    previousVendorCount: 71,
    filteredVendors: []
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadDecisionData();
    await loadVendorDatabase();
    renderAllQuestions();
    attachEventListeners();
    updateRecommendations(); // Initial state
});

// Load decision data from JSON
async function loadDecisionData() {
    try {
        const response = await fetch('decision-data-v2.json');
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

// Render all questions at once (single page view)
function renderAllQuestions() {
    const container = document.getElementById('questionsContainer');

    const questionsHTML = state.data.questions.map(question => {
        if (question.type === 'multi_choice') {
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

// Attach event listeners to all inputs
function attachEventListeners() {
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', handleOptionChange);
    });

    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleCheckboxChange);
    });

    document.getElementById('downloadBtn').addEventListener('click', downloadReport);
    document.getElementById('resetBtn').addEventListener('click', resetForm);
}

// Handle radio button selection
function handleOptionChange(event) {
    const questionId = event.target.name;
    const optionId = event.target.value;

    // Store answer
    state.answers[questionId] = optionId;

    // Visual feedback
    const questionGroup = document.querySelector(`[data-question-id="${questionId}"]`);
    questionGroup.querySelectorAll('.option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.target.closest('.option').classList.add('selected');

    // Update recommendations in real-time
    updateRecommendations();
}

// Handle checkbox change (multi-select for Q5)
function handleCheckboxChange(event) {
    const questionId = event.target.name;
    const optionId = event.target.value;

    if (questionId === 'q5_primary_use_case') {
        if (event.target.checked) {
            state.useCases.push(optionId);
        } else {
            state.useCases = state.useCases.filter(id => id !== optionId);
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

// Update recommendations based on current answers
function updateRecommendations() {
    // Filter vendors based on constraints
    filterVendors();

    // Derive isolation pattern from Q3
    const isolationPattern = deriveIsolationPattern();

    // Update recommendation sections
    updateArchitectureStack(isolationPattern);
    updatePerformanceTCO(isolationPattern);
    updateProductionExamples(isolationPattern);
    updateVendorRecommendations();

    // Enable download button if all required questions answered
    updateDownloadButton();
}

// ACTUAL VENDOR FILTERING LOGIC
function filterVendors() {
    let filtered = [...state.vendors];
    const answers = state.answers;

    // Q1: Team size filter
    if (answers.q1_team_size === 'lean') {
        // Lean teams need low operational complexity
        filtered = filtered.filter(v =>
            v.capabilities.operational_complexity === 'low' ||
            v.capabilities.managed_service_available === true
        );
    }

    // Q2: Budget filter
    if (answers.q2_budget === 'under_500k') {
        // Eliminate high-cost vendors (Unity Catalog, Databricks, Snowflake, Splunk)
        filtered = filtered.filter(v => {
            const costRange = v.typical_annual_cost_range.toLowerCase();
            // If cost range mentions millions or high values, filter out
            return !costRange.includes('$1m') &&
                   !costRange.includes('$2m') &&
                   !v.id.includes('databricks') &&
                   !v.id.includes('snowflake') &&
                   !v.id.includes('splunk');
        });
    }

    // Q3: Isolation pattern (affects catalog requirement)
    const isolationPattern = deriveIsolationPattern();
    if (isolationPattern === 'shared_corporate' || isolationPattern === 'multi_tenant_mssp') {
        // Shared platforms require Unity Catalog support
        filtered = filtered.filter(v =>
            v.capabilities.unity_catalog_support === true ||
            v.id === 'unity-catalog' ||
            v.id === 'databricks'
        );
    } else if (isolationPattern === 'isolated_dedicated') {
        // Isolated platforms prefer Polaris/Nessie compatible vendors
        filtered = filtered.filter(v =>
            v.capabilities.polaris_catalog_support === true ||
            v.capabilities.nessie_catalog_support === true ||
            v.capabilities.iceberg_support === true ||
            v.id === 'polaris' ||
            v.id === 'nessie'
        );
    }

    // Q4: Cloud environment filter
    if (answers.q4_cloud_environment === 'on_prem') {
        filtered = filtered.filter(v =>
            v.capabilities.deployment_models.includes('on-prem') ||
            v.capabilities.deployment_models.includes('hybrid')
        );
    } else if (answers.q4_cloud_environment === 'multi_cloud') {
        filtered = filtered.filter(v =>
            v.capabilities.multi_cloud === true
        );
    }

    // Q5: Use cases filter (multi-select)
    if (state.useCases.includes('real_time_dashboards')) {
        // Prioritize low-latency query engines
        filtered.forEach(v => {
            if (v.capabilities.query_latency_p95 && v.capabilities.query_latency_p95 < 1000) {
                v.score = (v.score || 0) + 3;  // Boost for low latency
            }
        });
    }

    // Q6: Table format preference
    if (answers.q6_table_format === 'iceberg') {
        filtered = filtered.filter(v => v.capabilities.iceberg_support === true);
    } else if (answers.q6_table_format === 'delta_lake') {
        filtered = filtered.filter(v => v.capabilities.delta_lake_support === true);
    }

    // Q7: Vendor tolerance
    if (answers.q7_vendor_tolerance === 'oss_first') {
        filtered = filtered.filter(v =>
            v.vendor_type === 'open_source' || v.cost_notes.toLowerCase().includes('oss') || v.cost_notes.toLowerCase().includes('open source')
        );
    } else if (answers.q7_vendor_tolerance === 'commercial_only') {
        filtered = filtered.filter(v =>
            v.vendor_type !== 'open_source'
        );
    }

    // Sort by score (if calculated) or alphabetically
    filtered.sort((a, b) => (b.score || 0) - (a.score || 0));

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

// Derive isolation pattern from Q3 (data co-location question)
function deriveIsolationPattern() {
    const dataColocation = state.answers.q3_data_colocatio;

    if (!dataColocation) return null;

    const question = state.data.questions.find(q => q.id === 'q3_data_colocatio');
    const option = question.options.find(opt => opt.id === dataColocation);

    return option ? option.isolation_pattern : null;
}

// Update architecture stack recommendations
function updateArchitectureStack(isolationPattern) {
    const answers = state.answers;

    // Isolation Pattern
    if (isolationPattern) {
        const patterns = {
            'isolated_dedicated': 'Isolated Dedicated (0% RLS overhead)',
            'shared_corporate': 'Shared Corporate (15-50% RLS overhead)',
            'multi_tenant_mssp': 'Multi-tenant MSSP (5-30% RLS overhead)'
        };
        document.getElementById('isolationPattern').textContent = patterns[isolationPattern] || 'Not determined';
    } else {
        document.getElementById('isolationPattern').textContent = 'Answer Q3 to determine';
    }

    // Catalog Recommendation
    let catalogRec = 'Answer Q2 & Q3';
    if (answers.q2_budget && isolationPattern) {
        if (answers.q2_budget === 'under_500k' && isolationPattern === 'isolated_dedicated') {
            catalogRec = 'Polaris or Nessie (OSS, $0)';
        } else if (isolationPattern === 'shared_corporate' || isolationPattern === 'multi_tenant_mssp') {
            catalogRec = 'Unity Catalog (REQUIRED for RLS)';
        } else if (isolationPattern === 'isolated_dedicated') {
            catalogRec = 'Polaris (vendor-neutral) or Nessie (Git workflows)';
        }
    }
    document.getElementById('catalogRec').textContent = catalogRec;

    // Table Format Recommendation
    let tableFormatRec = 'Answer Q3 & Q6';
    if (answers.q6_table_format) {
        const formats = {
            'iceberg': 'Apache Iceberg',
            'delta_lake': 'Delta Lake',
            'no_preference': isolationPattern === 'isolated_dedicated' ? 'Iceberg (recommended)' : 'Delta Lake or Iceberg'
        };
        tableFormatRec = formats[answers.q6_table_format] || 'Not selected';
    } else if (isolationPattern) {
        tableFormatRec = isolationPattern === 'isolated_dedicated' ? 'Iceberg (recommended)' : 'Delta Lake or Iceberg';
    }
    document.getElementById('tableFormatRec').textContent = tableFormatRec;

    // Query Engine Recommendation (based on multi-select use cases)
    let queryEngineRec = 'Answer Q5';
    if (state.useCases.length > 0) {
        const engines = [];
        if (state.useCases.includes('real_time_dashboards')) engines.push('ClickHouse');
        if (state.useCases.includes('ad_hoc_hunting')) engines.push('DuckDB');
        if (state.useCases.includes('compliance_reporting')) engines.push('Athena');
        if (state.useCases.includes('detection_rules')) engines.push('Kafka + Flink');

        queryEngineRec = engines.length > 0 ? engines.join(' + ') : 'Trino (flexible)';
    }
    document.getElementById('queryEngineRec').textContent = queryEngineRec;
}

// Update performance and TCO metrics
function updatePerformanceTCO(isolationPattern) {
    const answers = state.answers;
    const container = document.getElementById('performanceMetrics');

    if (!isolationPattern || !answers.q2_budget) {
        container.innerHTML = '<p style="color: #6b7280; font-size: 0.9rem;">Answer Q2 & Q3 for performance/cost estimates</p>';
        return;
    }

    const dataColocation = state.answers.q3_data_colocatio;
    const question = state.data.questions.find(q => q.id === 'q3_data_colocatio');
    const option = question.options.find(opt => opt.id === dataColocation);

    let performanceHTML = '';

    if (option.performance_gain) {
        performanceHTML += `<div class="performance-badge good">⚡ ${option.performance_gain}</div>`;
    } else if (option.performance_overhead) {
        const badgeClass = option.performance_overhead.includes('15-50') ? 'high' : 'moderate';
        performanceHTML += `<div class="performance-badge ${badgeClass}">⚠️ ${option.performance_overhead}</div>`;
    }

    performanceHTML += `<div class="performance-badge ${option.tco.includes('Low') ? 'good' : 'high'}">💰 TCO: ${option.tco}</div>`;

    container.innerHTML = performanceHTML;
}

// Update production examples
function updateProductionExamples(isolationPattern) {
    const container = document.getElementById('productionExamples');
    const list = document.getElementById('examplesList');

    if (!isolationPattern) {
        container.style.display = 'none';
        return;
    }

    const dataColocation = state.answers.q3_data_colocatio;
    const question = state.data.questions.find(q => q.id === 'q3_data_colocatio');
    const option = question.options.find(opt => opt.id === dataColocation);

    if (option && option.production_examples) {
        container.style.display = 'block';
        list.innerHTML = option.production_examples.map(ex => `<li>${ex}</li>`).join('');
    } else {
        container.style.display = 'none';
    }
}

// Update download button state
function updateDownloadButton() {
    const requiredQuestions = state.data.questions.filter(q => q.required).map(q => q.id);
    const allAnswered = requiredQuestions.every(qId => {
        if (qId === 'q5_primary_use_case') {
            return state.useCases.length > 0;
        }
        return state.answers[qId];
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

// Generate text report WITH VENDOR RECOMMENDATIONS
function generateTextReport() {
    const isolationPattern = deriveIsolationPattern();
    const topVendors = state.filteredVendors.slice(0, 5);

    return `
SECURITY DATA PLATFORM ARCHITECTURE RECOMMENDATION REPORT
==========================================================

Generated: ${new Date().toLocaleString()}
Tool: Security Data Platform Architecture Decision Tool (v2.0)
Source: Modern Data Stack for Cybersecurity by Jeremy Wiley

YOUR REQUIREMENTS
-----------------

Team Capacity: ${getAnswerLabel('q1_team_size')}
Budget: ${getAnswerLabel('q2_budget')}
Data Co-location: ${getAnswerLabel('q3_data_colocatio')}
Cloud Environment: ${getAnswerLabel('q4_cloud_environment')}
Primary Use Cases: ${state.useCases.map(id => getUseCaseLabel(id)).join(', ')}
Table Format Preference: ${getAnswerLabel('q6_table_format')}
Vendor Tolerance: ${getAnswerLabel('q7_vendor_tolerance')}

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

// Helper: Get answer label from question ID
function getAnswerLabel(questionId) {
    const answer = state.answers[questionId];
    if (!answer) return 'Not answered';

    const question = state.data.questions.find(q => q.id === questionId);
    if (!question) return 'Unknown';

    const option = question.options.find(opt => opt.id === answer);
    return option ? option.label : 'Unknown';
}

// Helper: Get use case label
function getUseCaseLabel(useCaseId) {
    const question = state.data.questions.find(q => q.id === 'q5_primary_use_case');
    if (!question) return useCaseId;

    const option = question.options.find(opt => opt.id === useCaseId);
    return option ? option.label : useCaseId;
}

// Reset form
function resetForm() {
    // Clear answers
    state.answers = {};
    state.useCases = [];
    state.vendorCount = state.vendors ? state.vendors.length : 71;
    state.previousVendorCount = state.vendorCount;
    state.filteredVendors = state.vendors ? [...state.vendors] : [];

    // Clear all radio/checkbox selections
    document.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(input => {
        input.checked = false;
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
