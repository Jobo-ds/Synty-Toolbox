# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Synty-Toolbox is a Blender addon designed for working with Synty game asset files. It provides a streamlined workflow for converting FBX assets to GLB format, organizing files, and preparing them for use in game engines like Godot.

## Architecture

### Module Structure
- **Main entry point**: `__init__.py` - Standard Blender addon registration
- **Class registration**: `register_classes.py` - Central registration of all UI classes, operators, and properties
- **Main UI**: `main_panel.py` - Primary sidebar panel in 3D Viewport under "Tool" tab
- **State management**: `state.py` - Simple global state (material counter)

### Core Modules
Each major feature is organized into its own module with consistent structure:

1. **fbx2glb/** - FBX to GLB conversion with material assignment
   - `operator.py` - Main conversion logic and batch processing
   - `ui.py` - Popup dialog for conversion settings
   - `properties.py` - Blender property definitions
   - `importers/fbx.py` - FBX import handling
   - `exporters/glb.py` - GLB export with material operations
   - `utils/` - Material operations, cleanup, ASCII warnings, corrections

2. **glb2blend/** - GLB to Blend file conversion
   - Simple recursive conversion with optional "-col" suffix for collision objects

3. **filesorter/** - Automatic file organization
   - Sorts FBX files into category folders based on naming conventions
   - Uses token mapping (Bld→Buildings, Wep→Weapons, etc.)

4. **simplifymat/** - Material optimization
   - Merges duplicate materials and simplifies material setups

5. **cleanblendforgodot/** - Godot-specific cleanup
   - Prepares blend files for Godot import

### Utility Modules (`utils/`)
- `blender.py` - Scene manipulation (clear_scene, object dimensions)
- `file_operations.py` - File system operations
- `folder_operations.py` - Directory management
- `memory.py` - Memory cleanup and optimization

## Development Commands

This is a Blender addon - no traditional build/test commands. Development workflow:

1. **Installation**: Copy entire folder to Blender addons directory
2. **Reload addon**: In Blender, disable and re-enable the addon in Preferences
3. **Testing**: Use the addon tools in Blender's 3D Viewport > Sidebar > Tool tab

## Key Patterns

### Blender Integration
- All operators inherit from `bpy.types.Operator`
- Properties use Blender's property system (`bpy.props.StringProperty`, etc.)
- UI classes inherit from `bpy.types.Panel` or create popup dialogs
- Scene properties are registered as pointer properties on `bpy.types.Scene`

### File Processing Workflow
1. **Input validation** - Check folder paths exist
2. **Batch processing** - Iterate through files/folders
3. **Scene management** - Clear scene before each file with `clear_scene()`
4. **Import/Export** - Use Blender's built-in operators
5. **Cleanup** - Purge unused data blocks to prevent memory leaks

### Naming Conventions
- Class prefix: `SSTOOL_` (all classes)
- Operator IDs: `sstool.operation_name`
- Property groups: `SSTOOL_PG_ModuleName`
- UI classes: `SSTOOL_OT_ModuleNamePopup` or `SSTOOL_PT_PanelName`

## Working with Synty Assets

The addon is specifically designed for Synty's asset naming conventions:
- Files with prefixes like "Bld_", "Wep_", "Env_" are automatically categorized
- Character files identified by "character" keyword or "_chr_"/"_char_" patterns
- Demo files separated into their own category
- Enhanced texture detection supports PNG, JPG, TGA, EXR and other formats
- Smart texture classification (diffuse, normal, roughness, metallic, emission)

## Enhanced Features (v2.0)

### Error Handling & Recovery
- Comprehensive logging system with different log levels
- Batch processing with continue-on-error support
- Retry mechanisms for failed imports
- Graceful fallback to error materials when processing fails

### Performance Optimizations
- Texture caching system to avoid reloading same textures
- Memory management with automatic cleanup
- Progress reporting for large batch operations
- Configurable cache clearing between folders

### Advanced Material System
- Modular material templates (Standard PBR, Emissive, Stylized, Error)
- Material factory pattern for consistent creation
- Support for multiple texture types (diffuse, normal, roughness, metallic, emission)
- Backward compatibility with legacy material operations

### File Detection & Validation
- Enhanced texture detection with confidence scoring
- FBX file validation (binary vs ASCII detection)
- Texture resolution and format validation
- Comprehensive file analysis and reporting

### User Experience Improvements
- Preview mode to analyze batch before processing
- Detailed processing logs and statistics
- Better error reporting with specific failure reasons
- Configurable processing options (retries, cache management)

## Development Guidelines

### Using the Enhanced System
- `FBXProcessingService` handles all batch processing logic
- `MaterialFactory` creates materials using template system
- `TextureCache` manages texture loading and memory
- `Logger` provides consistent logging across the addon

### Adding New Material Templates
1. Create new class inheriting from `BaseMaterial`
2. Implement `_build_nodes()` and `_setup_connections()`
3. Add template to `MaterialFactory.TEMPLATES`
4. Update UI enum property if needed

### Error Handling Best Practices
- Use logger for all informational and error messages
- Return `ProcessingResult` objects from processing functions
- Implement graceful degradation for non-critical failures
- Always clean up resources in finally blocks

## Memory Management

Enhanced memory management for large batch operations:
- Always call `clear_scene()` between file operations
- Use `purge_unused_data()` after batch operations
- Leverage `TextureCache` for efficient texture reuse
- Monitor cache statistics for performance optimization
- Properly unregister all classes and scene properties in `unregister()`