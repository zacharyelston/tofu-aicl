#!/usr/bin/env python3
"""
Generate architecture diagrams for AICL Keystore system
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_keystore_architecture():
    """Create the main keystore architecture diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define colors
    colors = {
        'aicl': '#2E86AB',
        'providers': '#A23B72', 
        'config': '#F18F01',
        'protection': '#C73E1D',
        'cloud': '#4CAF50'
    }
    
    # AICL Application Layer
    aicl_box = FancyBboxPatch((1, 8), 4, 2, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['aicl'], 
                              alpha=0.7, 
                              edgecolor='black')
    ax.add_patch(aicl_box)
    ax.text(3, 9, 'AICL Engine\n& Keystore Manager', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    
    # Provider Layer
    providers = [
        ('Azure Key Vault', 7, 8.5),
        ('AWS Secrets', 7, 7),
        ('Google Secrets', 7, 5.5),
        ('Local .env', 7, 4),
        ('Environment Vars', 7, 2.5)
    ]
    
    for name, x, y in providers:
        provider_box = FancyBboxPatch((x, y-0.4), 3.5, 0.8,
                                      boxstyle="round,pad=0.05",
                                      facecolor=colors['providers'],
                                      alpha=0.7,
                                      edgecolor='black')
        ax.add_patch(provider_box)
        ax.text(x+1.75, y, name, ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
        
        # Connection lines
        ax.plot([5, 7], [9, y], 'k--', alpha=0.6, linewidth=1)
    
    # Configuration Layer
    config_items = [
        ('keystore.yaml', 12, 8),
        ('.env.template', 12, 6.5),
        ('terraform/', 12, 5)
    ]
    
    for name, x, y in config_items:
        config_box = FancyBboxPatch((x, y-0.3), 2.5, 0.6,
                                    boxstyle="round,pad=0.05",
                                    facecolor=colors['config'],
                                    alpha=0.7,
                                    edgecolor='black')
        ax.add_patch(config_box)
        ax.text(x+1.25, y, name, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')
        
        # Connection to providers
        ax.plot([10.5, 12], [6.5, y], 'k:', alpha=0.6, linewidth=1)
    
    # LLM Protection Layer
    protection_box = FancyBboxPatch((1, 0.5), 8, 1.5,
                                    boxstyle="round,pad=0.1",
                                    facecolor=colors['protection'],
                                    alpha=0.7,
                                    edgecolor='black')
    ax.add_patch(protection_box)
    ax.text(5, 1.25, 'LLM Session Protection\nValidation Rules • Error Guidance • Simulation Prevention',
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    
    # Connection from AICL to Protection
    ax.plot([3, 5], [8, 2], 'r-', linewidth=2, alpha=0.8)
    
    # Add title and labels
    ax.text(7.5, 11, 'AICL Keystore Architecture', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    
    # Add layer labels
    ax.text(0.2, 9, 'Application\nLayer', ha='left', va='center', 
            fontsize=10, fontweight='bold', rotation=90)
    ax.text(0.2, 6, 'Provider\nLayer', ha='left', va='center',
            fontsize=10, fontweight='bold', rotation=90)
    ax.text(0.2, 1.25, 'Protection\nLayer', ha='left', va='center',
            fontsize=10, fontweight='bold', rotation=90)
    
    # Set axis properties
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/zacelston/code/tofu-aicl/docs/design/keystore-architecture.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_fallback_strategy():
    """Create the fallback strategy flowchart."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Define positions and connections for flowchart
    steps = [
        ('Key Request', 2, 9, 'start'),
        ('Primary Available?', 2, 7.5, 'decision'),
        ('Retrieve Primary', 5, 7.5, 'process'),
        ('Secondary Available?', 2, 6, 'decision'),
        ('Retrieve Secondary', 5, 6, 'process'),
        ('Local .env Available?', 2, 4.5, 'decision'),
        ('Load from .env', 5, 4.5, 'process'),
        ('Environment Vars?', 2, 3, 'decision'),
        ('Load from ENV', 5, 3, 'process'),
        ('FAIL with Error', 2, 1.5, 'error'),
        ('Cache Result', 8, 5.5, 'process'),
        ('Return Key', 11, 5.5, 'end'),
        ('Show LLM Instructions', 5, 1.5, 'process'),
        ('Prevent Simulation', 8, 1.5, 'process')
    ]
    
    colors = {
        'start': '#4CAF50',
        'decision': '#FF9800', 
        'process': '#2196F3',
        'error': '#F44336',
        'end': '#9C27B0'
    }
    
    # Draw boxes and text
    for name, x, y, type_name in steps:
        if type_name == 'decision':
            # Diamond shape for decisions
            diamond = patches.RegularPolygon((x, y), 4, radius=0.6, 
                                           orientation=np.pi/4,
                                           facecolor=colors[type_name],
                                           alpha=0.7, edgecolor='black')
            ax.add_patch(diamond)
        else:
            # Rectangle for other types
            width = 2.5 if len(name) > 15 else 2
            box = FancyBboxPatch((x-width/2, y-0.3), width, 0.6,
                                boxstyle="round,pad=0.05",
                                facecolor=colors[type_name],
                                alpha=0.7, edgecolor='black')
            ax.add_patch(box)
        
        # Add text
        fontsize = 9 if len(name) > 15 else 10
        ax.text(x, y, name, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color='white')
    
    # Add arrows for flow
    arrows = [
        ((2, 8.7), (2, 8.1)),  # Start to Primary
        ((2.6, 7.5), (4.4, 7.5)),  # Primary Yes
        ((2, 7.1), (2, 6.4)),  # Primary No
        ((2.6, 6), (4.4, 6)),  # Secondary Yes  
        ((2, 5.6), (2, 4.9)),  # Secondary No
        ((2.6, 4.5), (4.4, 4.5)),  # .env Yes
        ((2, 4.1), (2, 3.4)),  # .env No
        ((2.6, 3), (4.4, 3)),  # ENV Yes
        ((2, 2.6), (2, 1.9)),  # ENV No
        ((5, 7.2), (8, 5.8)),  # Primary to Cache
        ((5, 5.7), (8, 5.5)),  # Secondary to Cache
        ((5, 4.2), (8, 5.2)),  # .env to Cache
        ((5, 2.7), (8, 5.2)),  # ENV to Cache
        ((8.6, 5.5), (10.4, 5.5)),  # Cache to Return
        ((2.6, 1.5), (4.4, 1.5)),  # Error to Instructions
        ((5.6, 1.5), (7.4, 1.5))   # Instructions to Prevent
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    
    # Add Yes/No labels
    ax.text(3.5, 7.7, 'Yes', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(1.7, 6.8, 'No', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(3.5, 6.2, 'Yes', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(1.7, 5.3, 'No', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(3.5, 4.7, 'Yes', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(1.7, 3.8, 'No', ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(3.5, 3.2, 'Yes', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(1.7, 2.3, 'No', ha='center', va='center', fontsize=9, fontweight='bold')
    
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('AICL Keystore Fallback Strategy', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/Users/zacelston/code/tofu-aicl/docs/design/keystore-fallback-strategy.png',
                dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("🎨 Generating AICL Keystore Architecture Diagrams...")
    
    # Create diagrams
    create_keystore_architecture()
    print("✅ Main architecture diagram created")
    
    create_fallback_strategy() 
    print("✅ Fallback strategy diagram created")
    
    print("\n📊 Diagrams saved:")
    print("   - docs/design/keystore-architecture.png")
    print("   - docs/design/keystore-fallback-strategy.png")
    print("\n🎯 Ready for Redmine issue creation!")
