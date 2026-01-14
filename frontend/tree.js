let currentPersonId = null;
let searchTimeouts = {};

// Initialize tree view
async function initTreeView() {
    try {
        showLoading();
        const root = await api.getRoot();
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
        currentPersonId = personId;
        
        const data = await api.getNeighborhood(personId);
        
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
    
    children.forEach(child => {
        const card = createPersonCard(child, 'child');
        card.addEventListener('click', () => loadNeighborhood(child.id));
        section.appendChild(card);
    });
}

// Create person card
function createPersonCard(person, type, parentType = null) {
    const card = document.createElement('div');
    card.className = `person-card ${type}`;
    card.dataset.personId = person.id;
    
    const name = document.createElement('div');
    name.className = 'person-name';
    name.textContent = person.name;
    card.appendChild(name);
    
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
            // Single child: direct line
            const childRect = childCards[0].getBoundingClientRect();
            const childX = childRect.left + childRect.width / 2 - containerRect.left;
            const childY = childRect.top - containerRect.top;
            
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', centerX);
            line.setAttribute('y1', centerY);
            line.setAttribute('x2', childX);
            line.setAttribute('y2', childY);
            line.setAttribute('stroke', '#4a5568');
            line.setAttribute('stroke-width', '2');
            svg.appendChild(line);
        } else {
            // Multiple children: horizontal bus with vertical drops
            const childPositions = Array.from(childCards).map(card => {
                const rect = card.getBoundingClientRect();
                return {
                    x: rect.left + rect.width / 2 - containerRect.left,
                    y: rect.top - containerRect.top
                };
            });
            
            const minX = Math.min(...childPositions.map(p => p.x));
            const maxX = Math.max(...childPositions.map(p => p.x));
            const busY = centerY + 40; // Distance from center to bus line
            
            // Horizontal bus line
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
            
            // Vertical drops from bus to each child
            childPositions.forEach(pos => {
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
function initRelationshipView() {
    const person1Search = document.getElementById('person1-search');
    const person2Search = document.getElementById('person2-search');
    const findBtn = document.getElementById('find-relationship-btn');
    
    let person1 = null;
    let person2 = null;
    
    // Person 1 search
    person1Search.addEventListener('input', debounce(async (e) => {
        const query = e.target.value.trim();
        const resultsDiv = document.getElementById('person1-results');
        
        if (query.length < 2) {
            resultsDiv.innerHTML = '';
            return;
        }
        
        try {
            const data = await api.search(query);
            displaySearchResults(resultsDiv, data.results, (person) => {
                person1 = person;
                document.getElementById('person1-selected').textContent = `Selected: ${person.name}`;
                person1Search.value = '';
                resultsDiv.innerHTML = '';
                updateFindButton();
            });
        } catch (error) {
            console.error('Search failed:', error);
        }
    }, 300));
    
    // Person 2 search
    person2Search.addEventListener('input', debounce(async (e) => {
        const query = e.target.value.trim();
        const resultsDiv = document.getElementById('person2-results');
        
        if (query.length < 2) {
            resultsDiv.innerHTML = '';
            return;
        }
        
        try {
            const data = await api.search(query);
            displaySearchResults(resultsDiv, data.results, (person) => {
                person2 = person;
                document.getElementById('person2-selected').textContent = `Selected: ${person.name}`;
                person2Search.value = '';
                resultsDiv.innerHTML = '';
                updateFindButton();
            });
        } catch (error) {
            console.error('Search failed:', error);
        }
    }, 300));
    
    // Find relationship
    findBtn.addEventListener('click', async () => {
        if (!person1 || !person2) return;
        
        try {
            findBtn.disabled = true;
            findBtn.textContent = 'Finding...';
            
            const result = await api.getRelationship(person1.id, person2.id);
            displayRelationshipResult(result);
        } catch (error) {
            document.getElementById('relationship-result').innerHTML = 
                `<p class="error">Error: ${error.message}</p>`;
            document.getElementById('relationship-result').classList.remove('hidden');
        } finally {
            findBtn.disabled = false;
            findBtn.textContent = 'Show Relationship';
        }
    });
    
    function updateFindButton() {
        findBtn.disabled = !(person1 && person2);
    }
    
    function displaySearchResults(container, results, onSelect) {
        container.innerHTML = '';
        
        if (results.length === 0) {
            container.innerHTML = '<div class="search-result">No results found</div>';
            return;
        }
        
        results.forEach(person => {
            const div = document.createElement('div');
            div.className = 'search-result';
            div.textContent = person.name;
            div.addEventListener('click', () => onSelect(person));
            container.appendChild(div);
        });
    }
    
    function displayRelationshipResult(result) {
        const resultDiv = document.getElementById('relationship-result');
        const pathDiv = document.getElementById('relationship-path');
        
        if (!result.found) {
            pathDiv.innerHTML = '<p>No relationship found between these two people.</p>';
        } else {
            if (result.path.length === 0) {
                pathDiv.innerHTML = '<p>Same person selected.</p>';
            } else {
                const pathHtml = result.path.map((person, idx) => {
                    const arrow = idx < result.path.length - 1 ? ' → ' : '';
                    return `<span class="path-person">${person.name}</span>${arrow}`;
                }).join('');
                pathDiv.innerHTML = pathHtml;
                
                if (result.common_ancestor) {
                    pathDiv.innerHTML += `<p class="common-ancestor">Common Ancestor: ${result.common_ancestor.name}</p>`;
                }
            }
        }
        
        resultDiv.classList.remove('hidden');
    }
}

