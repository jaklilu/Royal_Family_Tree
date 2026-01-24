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
        const infoDiv = document.getElementById('relationship-info');
        
        visualization.classList.remove('hidden');
        
        console.log('Relationship result:', result); // Debug
        
        if (!result.found) {
            // No relationship found
            person1Card.innerHTML = '<div class="no-relationship">No relationship found</div>';
            person2Card.innerHTML = '';
            infoDiv.innerHTML = '<p class="error">These two people are not related in the family tree.</p>';
            return;
        }
        
        if (result.message === 'Same person') {
            // Same person selected
            person1Card.innerHTML = '<div class="same-person">Same person selected</div>';
            person2Card.innerHTML = '';
            infoDiv.innerHTML = '<p>You selected the same person twice.</p>';
            return;
        }
        
        // Display vertical trees: Person 1 lineage on left, Person 2 lineage on right, meeting at common ancestor
        const person1Lineage = result.person1_lineage || [];
        const person2Lineage = result.person2_lineage || [];
        const commonAncestor = result.common_ancestor;
        const siblingsInfo = result.siblings_info || null;
        
        console.log('Person1 lineage:', person1Lineage); // Debug
        console.log('Person2 lineage:', person2Lineage); // Debug
        console.log('Common ancestor:', commonAncestor); // Debug
        console.log('Siblings info:', siblingsInfo); // Debug
        
        const graphContainer = document.querySelector('.relationship-graph');
        if (commonAncestor && graphContainer) {
            graphContainer.classList.add('has-common-ancestor');
        } else if (graphContainer) {
            graphContainer.classList.remove('has-common-ancestor');
        }
        
        if (person1Lineage.length === 0 && person2Lineage.length === 0) {
            person1Card.innerHTML = '<div class="no-relationship">No lineage data available</div>';
            person2Card.innerHTML = '';
            infoDiv.innerHTML = '<p class="error">Unable to determine relationship paths.</p>';
            return;
        }
        
        // Find the index of common ancestor in both lineages to align them
        let person1CommonIdx = -1;
        let person2CommonIdx = -1;
        if (commonAncestor) {
            person1Lineage.forEach((p, idx) => {
                if (p.id === commonAncestor.id) person1CommonIdx = idx;
            });
            person2Lineage.forEach((p, idx) => {
                if (p.id === commonAncestor.id) person2CommonIdx = idx;
            });
        }
        
        // Render Person 1's lineage (left column: person at bottom, ancestors going up)
        if (person1Lineage.length > 0) {
            person1Card.innerHTML = '<div class="lineage-column left-lineage">' +
                person1Lineage.map((person, idx) => {
                    const isBottom = idx === 0; // First person is at bottom
                    const isCommonAncestor = commonAncestor && person.id === commonAncestor.id;
                    const isSibling = siblingsInfo && siblingsInfo.relationship === 'siblings' && person.id === siblingsInfo.person1.id;
                    const isCousin = siblingsInfo && siblingsInfo.relationship === 'cousins' && person.id === siblingsInfo.person1.id;
                    return renderLineageCard(person, idx, person1Lineage.length, 'left', isCommonAncestor, isBottom, isSibling, isCousin);
                }).join('') +
                '</div>';
        } else {
            person1Card.innerHTML = '<div class="no-relationship">No ancestors found</div>';
        }
        
        // Render connection bridge in the middle if there's a common ancestor
        let connectionBridge = '';
        if (commonAncestor && person1CommonIdx >= 0 && person2CommonIdx >= 0) {
            const maxHeight = Math.max(person1Lineage.length, person2Lineage.length);
            const commonHeight = Math.max(person1CommonIdx, person2CommonIdx);
            connectionBridge = `
                <div class="connection-bridge" style="grid-row: 1 / ${commonHeight + 2};">
                    <div class="bridge-line"></div>
                    <div class="bridge-meeting-point">
                        <div class="meeting-circle"></div>
                    </div>
                </div>
            `;
        }
        
        // Render connection bridge in the middle if there's a common ancestor
        const connectionBridgeEl = document.getElementById('connection-bridge');
        if (commonAncestor && person1CommonIdx >= 0 && person2CommonIdx >= 0 && connectionBridgeEl) {
            connectionBridgeEl.innerHTML = `
                <div class="bridge-line"></div>
                <div class="bridge-meeting-point">
                    <div class="meeting-circle"></div>
                </div>
            `;
            connectionBridgeEl.style.display = 'flex';
        } else if (connectionBridgeEl) {
            connectionBridgeEl.innerHTML = '';
            connectionBridgeEl.style.display = 'none';
        }
        
        // Render Person 2's lineage (right column: person at bottom, ancestors going up)
        if (person2Lineage.length > 0) {
            person2Card.innerHTML = '<div class="lineage-column right-lineage">' +
                person2Lineage.map((person, idx) => {
                    const isBottom = idx === 0; // First person is at bottom
                    const isCommonAncestor = commonAncestor && person.id === commonAncestor.id;
                    const isSibling = siblingsInfo && person.id === siblingsInfo.person2.id;
                    return renderLineageCard(person, idx, person2Lineage.length, 'right', isCommonAncestor, isBottom, isSibling);
                }).join('') +
                '</div>';
        } else {
            person2Card.innerHTML = '<div class="no-relationship">No ancestors found</div>';
        }
        
        // Display relationship info
        if (commonAncestor) {
            const ancestorName = commonAncestor.name_amharic || commonAncestor.name;
            const relationshipType = result.relationship_type || 'Related';
            
            let siblingsText = '';
            if (siblingsInfo) {
                const person1Name = siblingsInfo.person1.name_amharic || siblingsInfo.person1.name;
                const person2Name = siblingsInfo.person2.name_amharic || siblingsInfo.person2.name;
                const relationship = siblingsInfo.relationship || 'siblings';
                
                if (relationship === 'siblings') {
                    siblingsText = `
                        <p class="siblings-info">
                            <strong>Siblings:</strong> ${person1Name} and ${person2Name} 
                            (they share ${ancestorName} as their parent)
                        </p>
                    `;
                } else if (relationship === 'cousins') {
                    siblingsText = `
                        <p class="cousins-info">
                            <strong>Cousins:</strong> ${person1Name} and ${person2Name} 
                            (they share ${ancestorName} as their grandparent)
                        </p>
                    `;
                }
            }
            
            infoDiv.innerHTML = `
                <p class="common-ancestor-info">Common Ancestor: <strong>${ancestorName}</strong></p>
                ${siblingsText}
                <p class="relationship-type">Relationship: <strong>${relationshipType}</strong></p>
            `;
        } else {
            infoDiv.innerHTML = '<p>No common ancestor found in the displayed generations.</p>';
        }
    }
    
    function renderLineageCard(person, index, total, side, isCommonAncestor, isBottom, isSibling, isCousin) {
        const isTop = index === total - 1; // Last person (parent)
        
        let cardClass = 'lineage-person-card';
        if (isBottom) cardClass += ' selected-person-card';
        if (isCommonAncestor) cardClass += ' common-ancestor-card';
        if (isSibling) cardClass += ' sibling-card';
        if (isCousin) cardClass += ' cousin-card';
        
        const amharicName = person.name_amharic || '';
        const englishName = person.name || 'Unknown';
        
        let badge = '';
        if (isSibling) {
            badge = '<div class="sibling-badge">Sibling</div>';
        } else if (isCousin) {
            badge = '<div class="cousin-badge">Cousin</div>';
        }
        
        return `
            <div class="${cardClass} ${side}" data-person-id="${person.id}">
                ${badge}
                ${amharicName ? `<div class="lineage-card-name-amharic">${amharicName}</div>` : ''}
                <div class="lineage-card-name">${englishName}</div>
                ${!isTop ? '<div class="lineage-connector"></div>' : ''}
            </div>
        `;
    }
}

