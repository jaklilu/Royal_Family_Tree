let currentPersonId = null;
let previousPersonId = null; // Track the previous center person
let searchTimeouts = {};

// Update page title with person's name
function updatePageTitle(person) {
    const titleElement = document.getElementById('page-title');
    if (person) {
        // Prefer Amharic name for title, fallback to English
        const personName = person.name_amharic || person.name || person.name_original || 'Royal Family Tree';
        const titleText = `${personName} Family Tree`;
        
        // Update header title
        if (titleElement) {
            titleElement.textContent = titleText;
        }
        
        // Update browser tab title
        document.title = titleText;
    }
}

// Initialize tree view
async function initTreeView() {
    try {
        showLoading();
        const root = await api.getRoot();
        updatePageTitle(root);
        await loadNeighborhood(root.id);
    } catch (error) {
        showError('Failed to load family tree: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Load neighborhood for a person
async function loadNeighborhood(personId) {
    try {
        showLoading();
        // Track previous person before updating current
        previousPersonId = currentPersonId;
        currentPersonId = personId;
        
        const data = await api.getNeighborhood(personId);
        
        // Update page title with current person's name
        updatePageTitle(data.person);
        
        // Clear previous content
        clearTree();
        
        // Render sections
        if (data.parent) {
            renderParent(data.parent, data.parent_type);
        }
        
        renderPerson(data.person);
        renderChildren(data.children, data.is_leaf);
        
        // Draw connecting lines after a short delay to ensure DOM is ready
        setTimeout(() => {
            drawConnectingLines();
        }, 100);
        
        // Update URL (for sharing/bookmarking)
        window.location.hash = `#person/${personId}`;
        
    } catch (error) {
        showError('Failed to load person: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Clear tree view
function clearTree() {
    document.getElementById('parent-section').innerHTML = '';
    document.getElementById('center-section').innerHTML = '';
    document.getElementById('children-section').innerHTML = '';
    document.getElementById('tree-lines').innerHTML = '';
}

// Render parent card
function renderParent(parent, parentType) {
    const section = document.getElementById('parent-section');
    const card = createPersonCard(parent, 'parent', parentType);
    card.addEventListener('click', () => loadNeighborhood(parent.id));
    section.appendChild(card);
}

// Render selected person card
function renderPerson(person) {
    const section = document.getElementById('center-section');
    const card = createPersonCard(person, 'center');
    section.appendChild(card);
}

// Render children cards
function renderChildren(children, isLeaf) {
    const section = document.getElementById('children-section');
    
    // Remove any existing child count classes
    section.classList.remove('children-1', 'children-2', 'children-3', 'children-4', 'children-many');
    
    if (children.length === 0) {
        const emptyMsg = document.createElement('div');
        emptyMsg.className = 'empty-message';
        emptyMsg.textContent = 'No children recorded';
        if (isLeaf) {
            emptyMsg.textContent += ' (Attachment point for Phase 2)';
            emptyMsg.classList.add('leaf-indicator');
        }
        section.appendChild(emptyMsg);
        return;
    }
    
    // Add class based on number of children for dynamic width calculation
    if (children.length <= 4) {
        section.classList.add(`children-${children.length}`);
        console.log(`Added class: children-${children.length} for ${children.length} children`);
    } else {
        section.classList.add('children-many');
        console.log(`Added class: children-many for ${children.length} children`);
    }
    
    children.forEach(child => {
        const card = createPersonCard(child, 'child');
        // Add lighter green class if this was the previous center person
        if (previousPersonId && child.id === previousPersonId) {
            card.classList.add('previous-center');
        }
        card.addEventListener('click', () => loadNeighborhood(child.id));
        section.appendChild(card);
    });
}

// Create person card
function createPersonCard(person, type, parentType = null) {
    const card = document.createElement('div');
    card.className = `person-card ${type}`;
    card.dataset.personId = person.id;
    
    // Amharic name (top, primary focus - bold)
    if (person.name_amharic) {
        const nameAmharic = document.createElement('div');
        nameAmharic.className = 'person-name person-name-amharic';
        nameAmharic.textContent = person.name_amharic;
        card.appendChild(nameAmharic);
    }
    
    // English name (bottom, secondary - lighter)
    const nameEnglish = document.createElement('div');
    nameEnglish.className = 'person-name person-name-english';
    nameEnglish.textContent = person.name;
    card.appendChild(nameEnglish);
    
    if (parentType) {
        const label = document.createElement('div');
        label.className = 'parent-label';
        label.textContent = parentType === 'father' ? 'Father' : parentType === 'mother' ? 'Mother' : 'Parent';
        card.appendChild(label);
    }
    
    return card;
}

// Draw connecting lines (org-chart style)
function drawConnectingLines() {
    const svg = document.getElementById('tree-lines');
    svg.innerHTML = '';
    
    const parentCard = document.querySelector('.person-card.parent');
    const centerCard = document.querySelector('.person-card.center');
    const childCards = document.querySelectorAll('.person-card.child');
    
    if (!centerCard) return;
    
    const centerRect = centerCard.getBoundingClientRect();
    const containerRect = document.getElementById('tree-container').getBoundingClientRect();
    
    // Line from parent to center (if parent exists)
    if (parentCard) {
        const parentRect = parentCard.getBoundingClientRect();
        const parentX = parentRect.left + parentRect.width / 2 - containerRect.left;
        const parentY = parentRect.bottom - containerRect.top;
        const centerX = centerRect.left + centerRect.width / 2 - containerRect.left;
        const centerY = centerRect.top - containerRect.top;
        
        // Vertical line from parent to center
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', parentX);
        line.setAttribute('y1', parentY);
        line.setAttribute('x2', centerX);
        line.setAttribute('y2', centerY);
        line.setAttribute('stroke', '#4a5568');
        line.setAttribute('stroke-width', '2');
        svg.appendChild(line);
    }
    
    // Lines from center to children (if children exist)
    if (childCards.length > 0) {
        const centerX = centerRect.left + centerRect.width / 2 - containerRect.left;
        const centerY = centerRect.bottom - containerRect.top;
        
        if (childCards.length === 1) {
            // Single child: perfectly vertical line (use center card's X for both points)
            const childRect = childCards[0].getBoundingClientRect();
            const childX = childRect.left + childRect.width / 2 - containerRect.left;
            const childY = childRect.top - containerRect.top;
            
            // Use center card's X position to ensure perfectly vertical line
            // This ensures the line is straight even if child card is slightly off-center
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', centerX);
            line.setAttribute('y1', centerY);
            line.setAttribute('x2', centerX); // Use same X as center card for perfect vertical line
            line.setAttribute('y2', childY);
            line.setAttribute('stroke', '#4a5568');
            line.setAttribute('stroke-width', '2');
            svg.appendChild(line);
        } else {
            // Multiple children: horizontal bus with vertical drops to first row only (max 4 children)
            // Get only first row children (first 4)
            const firstRowChildren = Array.from(childCards).slice(0, 4);
            const firstRowPositions = firstRowChildren.map(card => {
                const rect = card.getBoundingClientRect();
                return {
                    x: rect.left + rect.width / 2 - containerRect.left,
                    y: rect.top - containerRect.top
                };
            });
            
            if (firstRowPositions.length > 0) {
                const minX = Math.min(...firstRowPositions.map(p => p.x));
                const maxX = Math.max(...firstRowPositions.map(p => p.x));
                const busY = centerY + 40; // Distance from center to bus line
                
                // Horizontal bus line (only across first row)
                const busLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                busLine.setAttribute('x1', minX);
                busLine.setAttribute('y1', busY);
                busLine.setAttribute('x2', maxX);
                busLine.setAttribute('y2', busY);
                busLine.setAttribute('stroke', '#4a5568');
                busLine.setAttribute('stroke-width', '2');
                svg.appendChild(busLine);
                
                // Vertical line from center to bus
                const centerToBus = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                centerToBus.setAttribute('x1', centerX);
                centerToBus.setAttribute('y1', centerY);
                centerToBus.setAttribute('x2', centerX);
                centerToBus.setAttribute('y2', busY);
                centerToBus.setAttribute('stroke', '#4a5568');
                centerToBus.setAttribute('stroke-width', '2');
                svg.appendChild(centerToBus);
                
                // Vertical drops from bus to each child in first row only (max 4)
                firstRowPositions.forEach(pos => {
                    const dropLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    dropLine.setAttribute('x1', pos.x);
                    dropLine.setAttribute('y1', busY);
                    dropLine.setAttribute('x2', pos.x);
                    dropLine.setAttribute('y2', pos.y);
                    dropLine.setAttribute('stroke', '#4a5568');
                    dropLine.setAttribute('stroke-width', '2');
                    svg.appendChild(dropLine);
                });
            }
        }
    }
    
    // Update SVG size to match container
    svg.setAttribute('width', containerRect.width);
    svg.setAttribute('height', containerRect.height);
}

// Handle window resize
window.addEventListener('resize', debounce(() => {
    if (currentPersonId) {
        drawConnectingLines();
    }
}, 250));

// Handle hash change (for back button)
window.addEventListener('hashchange', () => {
    const match = window.location.hash.match(/#person\/([^/]+)/);
    if (match) {
        loadNeighborhood(match[1]);
    }
});

// Loading and error states
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showError(message) {
    const errorEl = document.getElementById('error');
    errorEl.textContent = message;
    errorEl.classList.remove('hidden');
    document.getElementById('loading').classList.add('hidden');
}

// Initialize relationship view
let allPeople = [];
let person1Data = null;
let person2Data = null;

async function initRelationshipView() {
    const person1Select = document.getElementById('person1-select');
    const person2Select = document.getElementById('person2-select');
    const findBtn = document.getElementById('find-relationship-btn');
    
    // Load all people for dropdowns
    try {
        const data = await api.getAllPeople();
        allPeople = data.people || [];
        populateDropdowns(person1Select, person2Select);
    } catch (error) {
        console.error('Failed to load people:', error);
        showError('Failed to load people list');
    }
    
    // Person 1 selection
    person1Select.addEventListener('change', (e) => {
        const personId = e.target.value;
        if (personId) {
            person1Data = allPeople.find(p => p.id === personId);
            updateFindButton();
        } else {
            person1Data = null;
            updateFindButton();
        }
    });
    
    // Person 2 selection
    person2Select.addEventListener('change', (e) => {
        const personId = e.target.value;
        if (personId) {
            person2Data = allPeople.find(p => p.id === personId);
            updateFindButton();
        } else {
            person2Data = null;
            updateFindButton();
        }
    });
    
    // Find relationship
    findBtn.addEventListener('click', async () => {
        if (!person1Data || !person2Data) return;
        
        try {
            findBtn.disabled = true;
            findBtn.textContent = 'Finding...';
            
            const result = await api.getRelationship(person1Data.id, person2Data.id);
            displayRelationshipVisualization(result);
        } catch (error) {
            const visualization = document.getElementById('relationship-visualization');
            visualization.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            visualization.classList.remove('hidden');
        } finally {
            findBtn.disabled = false;
            findBtn.textContent = 'Find Relationship';
        }
    });
    
    function updateFindButton() {
        findBtn.disabled = !(person1Data && person2Data);
    }
    
    function populateDropdowns(select1, select2) {
        // Clear existing options (except first option)
        select1.innerHTML = '<option value="">-- Select Person --</option>';
        select2.innerHTML = '<option value="">-- Select Person --</option>';
        
        allPeople.forEach(person => {
            const displayName = person.name_amharic 
                ? `${person.name_amharic} (${person.name})`
                : person.name;
            
            const option1 = document.createElement('option');
            option1.value = person.id;
            option1.textContent = displayName;
            select1.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = person.id;
            option2.textContent = displayName;
            select2.appendChild(option2);
        });
    }
    
    function displayRelationshipVisualization(result) {
        const visualization = document.getElementById('relationship-visualization');
        const person1Card = document.getElementById('person1-card');
        const person2Card = document.getElementById('person2-card');
        const pathContainer = document.getElementById('relationship-path-container');
        const infoDiv = document.getElementById('relationship-info');
        
        visualization.classList.remove('hidden');
        
        // Display Person 1 card (left)
        renderPersonCard(person1Card, person1Data, 'left');
        
        // Display Person 2 card (right)
        renderPersonCard(person2Card, person2Data, 'right');
        
        if (!result.found) {
            pathContainer.innerHTML = '<div class="no-relationship">No relationship found</div>';
            infoDiv.innerHTML = '<p class="error">These two people are not related in the family tree.</p>';
        } else if (result.path.length === 0) {
            pathContainer.innerHTML = '<div class="same-person">Same person selected</div>';
            infoDiv.innerHTML = '<p>You selected the same person twice.</p>';
        } else {
            // Display path in center
            // result.path contains objects with {id, name}
            const pathPeople = result.path.map(pathPerson => {
                return allPeople.find(p => p.id === pathPerson.id) || {
                    id: pathPerson.id,
                    name: pathPerson.name || 'Unknown',
                    name_amharic: null
                };
            });
            
            // Remove person1 and person2 from path (they're already displayed on sides)
            const middlePath = pathPeople.filter(p => 
                p.id !== person1Data.id && p.id !== person2Data.id
            );
            
            if (middlePath.length === 0) {
                // Direct relationship (parent-child or siblings)
                pathContainer.innerHTML = '<div class="direct-relationship">Direct Relationship</div>';
            } else {
                // Display connecting people
                pathContainer.innerHTML = middlePath.map((person, idx) => {
                    const displayName = person.name_amharic || person.name;
                    return `
                        <div class="path-person-card">
                            <div class="path-person-name-amharic">${person.name_amharic || ''}</div>
                            <div class="path-person-name">${person.name}</div>
                        </div>
                        ${idx < middlePath.length - 1 ? '<div class="path-arrow">→</div>' : ''}
                    `;
                }).join('');
            }
            
            // Display relationship info
            if (result.common_ancestor) {
                const ancestorName = result.common_ancestor.name_amharic || result.common_ancestor.name;
                infoDiv.innerHTML = `<p class="common-ancestor-info">Common Ancestor: <strong>${ancestorName}</strong></p>`;
            } else {
                infoDiv.innerHTML = `<p>Relationship path found (${result.path.length} steps)</p>`;
            }
        }
    }
    
    function renderPersonCard(container, person, side) {
        const displayName = person.name_amharic || person.name;
        const englishName = person.name;
        container.innerHTML = `
            <div class="relationship-card ${side}">
                <div class="relationship-card-name-amharic">${person.name_amharic || ''}</div>
                <div class="relationship-card-name">${englishName}</div>
            </div>
        `;
    }
}

