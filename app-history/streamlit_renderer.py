import streamlit as st
import re
import uuid
import streamlit.components.v1 as components

# -------- RENDER MERMAID AND MARKDOWN ----------
def render_mermaid(code: str, height: int = 400):
    unique_id = f"mermaid-{uuid.uuid4().hex[:8]}"
    
    # We set width: 100% on the container and the internal div
    html_code = f"""
    <div id="container-{unique_id}" style="border: 1px solid #ddd; border-radius: 8px; width: 100%; height: {height}px; background: white;">
        <div id="{unique_id}" class="mermaid" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
            {code}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        
        // Initialize with useMaxWidth: false so we can control it manually
        mermaid.initialize({{ 
            startOnLoad: false, 
            theme: 'default',
            securityLevel: 'loose',
        }});

        const renderDiagram = async () => {{
            const element = document.getElementById("{unique_id}");
            const graphDefinition = `{code}`;
            
            // Render the diagram
            const {{ svg }} = await mermaid.render('svg-{unique_id}', graphDefinition);
            element.innerHTML = svg;

            const svgElement = element.querySelector('svg');
            
            // --- THE FIX: Remove Mermaid's hardcoded dimensions ---
            svgElement.style.width = '100%';
            svgElement.style.height = '100%';
            svgElement.style.maxWidth = '100%';
            svgElement.removeAttribute('height'); 
            
            // Initialize Pan & Zoom
            window.panZoom = svgPanZoom(svgElement, {{
                zoomEnabled: true,
                controlIconsEnabled: true,
                fit: true,
                center: true,
                minZoom: 0.1,
                maxZoom: 10
            }});
        }};

        renderDiagram();
    </script>
    """
    # Use use_container_width logic or set width to None to fill the Streamlit column
    components.html(html_code, height=height + 20)

def render_hybrid_response(text: str):
    # Regex to find mermaid blocks: ```mermaid ... ```
    parts = re.split(r'(```mermaid\n.*?\n```)', text, flags=re.DOTALL)
    
    for part in parts:
        if part.startswith("```mermaid"):
            # Strip the backticks and 'mermaid' keyword to get raw code
            clean_code = part.replace("```mermaid\n", "").replace("```", "")
            render_mermaid(clean_code)
        else:
            # It's just regular markdown
            st.markdown(part)
