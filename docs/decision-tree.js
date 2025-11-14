// Decision Tree Interactive Logic
//==============================================================================

// State Management
const decisionState = {
    data: null,
    answers: {},
    currentQuestionIndex: 0,
    vendorCount: 71 // Initial count from database
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadDecisionData();
    renderCurrentQuestion();
    updateProgress();
});

// Load decision data from JSON
async function loadDecisionData() {
    try {
        const response = await fetch('decision-data.json');
        decisionState.data = await response.json();
        document.getElementById('totalQuestions').textContent = decisionState.data.questions.length;
    } catch (error) {
        console.error('Error loading decision data:', error);
        alert('Failed to load decision tree data. Please refresh the page.');
    }
}

// Render current question
function renderCurrentQuestion() {
    const question = decisionState.data.questions[decisionState.currentQuestionIndex];
    if (!question) {
        showRecommendations();
        return;
    }

    const container = document.getElementById('questionContainer');
    container.innerHTML = `
        <div class="question">
            <div class="question-header">
                <div class="question-number">Question ${question.order} of ${decisionState.data.questions.length}</div>
                <h2 class="question-title">${question.title}</h2>
                <p class="question-description">${question.description}</p>
                ${question.context ? `<p class="question-context">💡 ${question.context}</p>` : ''}
            </div>

            <div class="options" id="options-${question.id}">
                ${renderOptions(question)}
            </div>
        </div>
    `;

    // Add event listeners to options
    attachOptionListeners(question);
}

// Render options for a question
function renderOptions(question) {
    return question.options.map(option => `
        <div class="option" data-option-id="${option.id}" onclick="selectOption('${question.id}', '${option.id}')">
            <input type="radio" name="${question.id}" value="${option.id}"
                   ${decisionState.answers[question.id] === option.id ? 'checked' : ''}>
            <label class="option-label">${option.label}</label>
            <p class="option-description">${option.description}</p>
            ${option.impact ? `<span class="option-impact">💡 ${option.impact}</span>` : ''}
            ${renderOptionMeta(option)}
        </div>
    `).join('');
}

// Render option metadata
function renderOptionMeta(option) {
    const parts = [];

    if (option.vendor_count_estimate) {
        parts.push(`<span>📊 ~${option.vendor_count_estimate} vendors compatible</span>`);
    }

    if (option.recommendations && option.recommendations.performance_overhead) {
        const overhead = option.recommendations.performance_overhead;
        const badgeClass = overhead === '0%' ? 'good' : overhead.includes('15-50') ? 'high' : 'moderate';
        parts.push(`<span class="performance-badge ${badgeClass}">⚡ ${overhead} RLS overhead</span>`);
    }

    if (option.recommendations && option.recommendations.tco) {
        parts.push(`<span>💰 ${option.recommendations.tco}</span>`);
    }

    return parts.length > 0 ? `<div class="option-meta">${parts.join('')}</div>` : '';
}

// Attach event listeners to option inputs
function attachOptionListeners(question) {
    const options = document.querySelectorAll(`#options-${question.id} .option`);
    options.forEach(option => {
        const input = option.querySelector('input');
        if (input) {
            input.addEventListener('change', () => {
                selectOption(question.id, input.value);
            });
        }
    });
}

// Handle option selection
function selectOption(questionId, optionId) {
    // Store answer
    decisionState.answers[questionId] = optionId;

    // Visual feedback
    const optionsContainer = document.querySelector(`#options-${questionId}`);
    const options = optionsContainer.querySelectorAll('.option');
    options.forEach(opt => {
        opt.classList.remove('selected');
        if (opt.dataset.optionId === optionId) {
            opt.classList.add('selected');
        }
    });

    // Update progress
    updateProgress();

    // Auto-advance after short delay
    setTimeout(() => {
        nextQuestion();
    }, 800);
}

// Move to next question
function nextQuestion() {
    if (decisionState.currentQuestionIndex < decisionState.data.questions.length - 1) {
        decisionState.currentQuestionIndex++;
        renderCurrentQuestion();
        updateProgress();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        showRecommendations();
    }
}

// Update progress bar
function updateProgress() {
    const answeredCount = Object.keys(decisionState.answers).length;
    const totalQuestions = decisionState.data.questions.length;
    const progress = (answeredCount / totalQuestions) * 100;

    const progressBar = document.getElementById('progressBar');
    progressBar.style.setProperty('--progress', `${progress}%`);

    document.getElementById('currentQuestion').textContent = answeredCount;
}

// Show final recommendations
function showRecommendations() {
    const container = document.getElementById('recommendationContainer');
    const questionContainer = document.getElementById('questionContainer');

    questionContainer.style.display = 'none';
    container.style.display = 'block';

    const recommendations = generateRecommendations();
    container.querySelector('#recommendationContent').innerHTML = recommendations;

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Generate recommendation content based on answers
function generateRecommendations() {
    const isolationPattern = decisionState.answers['f0_isolation_pattern'];
    const tableFormat = decisionState.answers['f1_table_format'];
    const catalog = decisionState.answers['f2_catalog'];
    const transformation = decisionState.answers['f3_transformation'];
    const queryEngine = decisionState.answers['f4_query_engine'];

    // Get selected options data
    const isolationData = getOptionData('f0_isolation_pattern', isolationPattern);
    const tableData = getOptionData('f1_table_format', tableFormat);
    const catalogData = getOptionData('f2_catalog', catalog);
    const transformData = getOptionData('f3_transformation', transformation);
    const queryData = getOptionData('f4_query_engine', queryEngine);

    const rec = isolationData?.recommendations || {};

    return `
        <div class="recommendation-section">
            <h3>🏗️ Your Architecture Stack</h3>
            <div class="recommendation-item">
                <span class="recommendation-label">Infrastructure Pattern:</span>
                <span class="recommendation-value">${isolationData?.label || 'Not selected'}</span>
            </div>
            <div class="recommendation-item">
                <span class="recommendation-label">Table Format:</span>
                <span class="recommendation-value">${tableData?.label || 'Not selected'}</span>
            </div>
            <div class="recommendation-item">
                <span class="recommendation-label">Catalog:</span>
                <span class="recommendation-value">${catalogData?.label || 'Not selected'}</span>
            </div>
            <div class="recommendation-item">
                <span class="recommendation-label">Transformation:</span>
                <span class="recommendation-value">${transformData?.label || 'Not selected'}</span>
            </div>
            <div class="recommendation-item">
                <span class="recommendation-label">Query Engine:</span>
                <span class="recommendation-value">${queryData?.label || 'Not selected'}</span>
            </div>
        </div>

        ${rec.catalog ? `
        <div class="recommendation-section">
            <h3>📋 Recommended Catalog Options</h3>
            <p>${rec.catalog.join(', ')}</p>
        </div>
        ` : ''}

        ${rec.performance_overhead ? `
        <div class="recommendation-section">
            <h3>⚡ Performance Impact</h3>
            <div class="recommendation-item">
                <span class="performance-badge ${rec.performance_overhead === '0%' ? 'good' : 'high'}">
                    ${rec.performance_overhead} RLS Overhead
                </span>
                ${rec.performance_overhead === '0%' ?
                    '<p style="margin-top: 12px; color: #065f46;">🎉 <strong>Isolation-first security enables 15-50% faster queries</strong> by avoiding row-level security, column masking, and metadata encryption overhead. Your security infrastructure isolation provides the security boundary.</p>' :
                    '<p style="margin-top: 12px; color: #991b1b;">⚠️ <strong>Shared platform requires fine-grained access control.</strong> Row-level security, column masking, and metadata encryption add overhead but are essential for compliance.</p>'}
            </div>
        </div>
        ` : ''}

        ${rec.tco ? `
        <div class="recommendation-section">
            <h3>💰 Total Cost of Ownership (5-year)</h3>
            <p><strong>${rec.tco}</strong></p>
            ${rec.performance_overhead === '0%' ?
                '<p style="margin-top: 8px; font-size: 0.95rem; color: #4b5563;">Open-source catalogs (Polaris, Nessie) eliminate licensing costs. Baseline compute with no RLS overhead reduces infrastructure spend by 15-30%.</p>' : ''}
        </div>
        ` : ''}

        ${rec.production_examples ? `
        <div class="recommendation-section">
            <h3>🏢 Production Validation</h3>
            <p>This architecture pattern is validated by:</p>
            <ul style="margin-top: 10px; margin-left: 20px; color: #4b5563;">
                ${rec.production_examples.map(ex => `<li>${ex}</li>`).join('')}
            </ul>
        </div>
        ` : ''}

        <div class="recommendation-section">
            <h3>📖 Next Steps</h3>
            <ol style="margin-left: 20px; color: #4b5563; line-height: 1.8;">
                <li><strong>Read detailed analysis:</strong> <a href="https://securitydatacommons.substack.com" target="_blank" style="color: #2563eb;">Security Data Commons Blog</a></li>
                <li><strong>Download architecture report:</strong> Click "Download Report" above for vendor analysis</li>
                <li><strong>Validate with production examples:</strong> Research how ${rec.production_examples?.[0] || 'Netflix'} implemented this pattern</li>
                <li><strong>Calculate TCO:</strong> Use the TCO calculator tool for 5-year cost projections</li>
            </ol>
        </div>

        <div class="recommendation-section">
            <h3>⚖️ Trade-offs to Consider</h3>
            ${generateTradeoffs(isolationPattern, catalog, queryEngine)}
        </div>
    `;
}

// Generate trade-offs based on selections
function generateTradeoffs(isolationPattern, catalog, queryEngine) {
    const tradeoffs = [];

    if (isolationPattern === 'isolated_dedicated') {
        tradeoffs.push('<li><strong>✅ Simplicity:</strong> Table-level RBAC is simpler to manage than row-level security policies</li>');
        tradeoffs.push('<li><strong>✅ Performance:</strong> 15-50% faster queries without RLS overhead</li>');
        tradeoffs.push('<li><strong>⚠️ Governance:</strong> If security data eventually co-locates with corporate data, you\'ll need to migrate to Unity Catalog</li>');
    } else if (isolationPattern === 'shared_corporate') {
        tradeoffs.push('<li><strong>✅ Governance:</strong> Strong fine-grained access control for compliance</li>');
        tradeoffs.push('<li><strong>⚠️ Performance:</strong> 15-50% query overhead from RLS + column masking</li>');
        tradeoffs.push('<li><strong>⚠️ Cost:</strong> Unity Catalog licensing ($10K-50K/year) + additional compute</li>');
    } else if (isolationPattern === 'multi_tenant_mssp') {
        tradeoffs.push('<li><strong>✅ Tenant Isolation:</strong> Essential row-level security for customer data separation</li>');
        tradeoffs.push('<li><strong>✅ Compliance:</strong> Meets multi-tenant MSSP regulatory requirements</li>');
        tradeoffs.push('<li><strong>⚠️ Cost:</strong> High TCO, but essential for business model</li>');
    }

    return `<ul style="margin-left: 20px; color: #4b5563; line-height: 1.8;">${tradeoffs.join('')}</ul>`;
}

// Get option data by question and option ID
function getOptionData(questionId, optionId) {
    const question = decisionState.data.questions.find(q => q.id === questionId);
    if (!question) return null;
    return question.options.find(opt => opt.id === optionId);
}

// Download report as text file
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

// Generate text report
function generateTextReport() {
    const isolationPattern = decisionState.answers['f0_isolation_pattern'];
    const tableFormat = decisionState.answers['f1_table_format'];
    const catalog = decisionState.answers['f2_catalog'];
    const transformation = decisionState.answers['f3_transformation'];
    const queryEngine = decisionState.answers['f4_query_engine'];

    const isolationData = getOptionData('f0_isolation_pattern', isolationPattern);
    const tableData = getOptionData('f1_table_format', tableFormat);
    const catalogData = getOptionData('f2_catalog', catalog);
    const transformData = getOptionData('f3_transformation', transformation);
    const queryData = getOptionData('f4_query_engine', queryEngine);

    const rec = isolationData?.recommendations || {};

    return `
SECURITY DATA PLATFORM ARCHITECTURE RECOMMENDATION REPORT
==========================================================

Generated: ${new Date().toLocaleString()}
Tool: Security Data Platform Architecture Decision Tool
Source: Modern Data Stack for Cybersecurity by Jeremy Wiley

YOUR ARCHITECTURE STACK
-----------------------

Infrastructure Pattern: ${isolationData?.label || 'Not selected'}
Table Format: ${tableData?.label || 'Not selected'}
Catalog: ${catalogData?.label || 'Not selected'}
Transformation: ${transformData?.label || 'Not selected'}
Query Engine: ${queryData?.label || 'Not selected'}

PERFORMANCE IMPACT
------------------

RLS Overhead: ${rec.performance_overhead || 'N/A'}
${rec.performance_overhead === '0%' ?
'✓ Isolation-first security enables 15-50% faster queries by avoiding row-level security overhead.' :
'⚠ Shared platform requires fine-grained access control with 15-50% performance overhead.'}

TOTAL COST OF OWNERSHIP (5-YEAR)
---------------------------------

${rec.tco || 'N/A'}

PRODUCTION VALIDATION
---------------------

This architecture pattern is validated by:
${rec.production_examples ? rec.production_examples.map(ex => `• ${ex}`).join('\n') : 'No examples available'}

NEXT STEPS
----------

1. Read detailed analysis: https://securitydatacommons.substack.com
2. Research production examples
3. Calculate detailed TCO for your data volume
4. Conduct proof-of-concept testing

DISCLAIMERS
-----------

• No vendor sponsorships - all recommendations evidence-based
• Validate cost estimates with vendors directly
• Test architecture patterns before production deployment
• Consult security/compliance teams for regulatory requirements

Report generated by Security Data Platform Architecture Decision Tool
https://flying-coyote.github.io/security-architect-mcp-server/
    `.trim();
}

// Reset decision tree
function resetDecisionTree() {
    decisionState.answers = {};
    decisionState.currentQuestionIndex = 0;

    document.getElementById('questionContainer').style.display = 'block';
    document.getElementById('recommendationContainer').style.display = 'none';

    renderCurrentQuestion();
    updateProgress();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
