#!/usr/bin/env python3
"""
control_panel.py - PyQt5 control panel interface

Enhanced control panel with tabbed interface, settings management,
and real-time pet monitoring with professional UI design.
"""

from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                           QComboBox, QLabel, QTabWidget, QHBoxLayout, QSlider, 
                           QCheckBox, QSpinBox, QGroupBox, QTextEdit, QSplitter)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import TYPE_CHECKING, List, Dict, Any

from config import AppConstants, get_config
from sprite_loader import SpriteDiscovery

if TYPE_CHECKING:
    from gui_manager import PygameWindow


class ControlPanel(QMainWindow):
    """Enhanced control panel with tabbed interface and settings"""
    
    # Signals for better event handling
    pet_spawned = pyqtSignal(str, str)  # sprite_name, pet_id
    pet_killed = pyqtSignal(str)        # pet_id
    settings_changed = pyqtSignal(str, object)  # setting_name, value
    
    def __init__(self, pygame_window: 'PygameWindow'):
        super().__init__()
        
        self.pygame_window = pygame_window
        self.config = get_config()
        self.sprite_packs = SpriteDiscovery.discover_sprite_packs()
        
        # Update config with discovered sprite packs
        self.config.set('sprite_packs', self.sprite_packs)
        
        # UI update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second
        
        self._setup_window()
        self._setup_ui()
        self._load_settings()
        
        print(f"Control panel initialized with {len(self.sprite_packs)} sprite packs")
    
    def _setup_window(self) -> None:
        """Setup window properties and geometry"""
        self.setWindowTitle(f"{AppConstants.APP_NAME} - Control Panel")
        
        # Load saved position and size
        x = self.config.get('ui.control_panel_x', 100)
        y = self.config.get('ui.control_panel_y', 100)
        width, height = AppConstants.CONTROL_PANEL_DEFAULT_SIZE
        
        self.setGeometry(x, y, width, height)
        self.setMinimumSize(*AppConstants.CONTROL_PANEL_MIN_SIZE)
    
    def _setup_ui(self) -> None:
        """Create the complete tabbed interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create all tabs
        self._create_pet_management_tab()
        self._create_settings_tab()
        self._create_monitoring_tab()
        self._create_about_tab()
    
    def _create_pet_management_tab(self) -> None:
        """Create pet management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Sprite selection group
        sprite_group = QGroupBox("Sprite Selection")
        sprite_layout = QVBoxLayout(sprite_group)
        
        sprite_layout.addWidget(QLabel("Select Sprite Pack:"))
        self.sprite_combo = QComboBox()
        if self.sprite_packs:
            self.sprite_combo.addItems(self.sprite_packs)
            # Set saved selection
            saved_sprite = self.config.get('ui.selected_sprite')
            if saved_sprite and saved_sprite in self.sprite_packs:
                self.sprite_combo.setCurrentText(saved_sprite)
        else:
            self.sprite_combo.addItem("No sprites found")
        self.sprite_combo.currentTextChanged.connect(self._on_sprite_changed)
        sprite_layout.addWidget(self.sprite_combo)
        
        layout.addWidget(sprite_group)
        
        # Pet actions group
        actions_group = QGroupBox("Pet Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Spawn controls
        spawn_layout = QHBoxLayout()
        spawn_btn = QPushButton("Spawn Pet")
        spawn_btn.clicked.connect(self._spawn_pet)
        spawn_layout.addWidget(spawn_btn)
        
        self.spawn_count_spin = QSpinBox()
        self.spawn_count_spin.setRange(1, 10)
        self.spawn_count_spin.setValue(1)
        spawn_layout.addWidget(QLabel("Count:"))
        spawn_layout.addWidget(self.spawn_count_spin)
        actions_layout.addLayout(spawn_layout)
        
        # Kill all button
        kill_all_btn = QPushButton("Kill All Pets")
        kill_all_btn.clicked.connect(self._kill_all_pets)
        kill_all_btn.setStyleSheet("QPushButton { background-color: #ff6b6b; }")
        actions_layout.addWidget(kill_all_btn)
        
        layout.addWidget(actions_group)
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel(f"Found {len(self.sprite_packs)} sprite pack(s)")
        status_layout.addWidget(self.status_label)
        
        self.pet_count_label = QLabel("Active pets: 0")
        status_layout.addWidget(self.pet_count_label)
        
        self.performance_label = QLabel("FPS: --")
        status_layout.addWidget(self.performance_label)
        
        layout.addWidget(status_group)
        
        # Controls info
        info_group = QGroupBox("Controls")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel(
            "• Left-click + drag to move pets (now with throw physics!)\n"
            "• Double right-click to kill individual pet\n"
            "• Single right-click to make pet sit / special actions\n"
            "• F1 to toggle debug mode\n"
            "• F2 to print performance info\n"
            "• Settings are auto-saved"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        self.tab_widget.addTab(tab, "Pet Management")
    
    def _create_settings_tab(self) -> None:
        """Create settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # General settings group
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout(general_group)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.config.get('settings.volume', 70))
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        self.volume_label = QLabel(f"{self.volume_slider.value()}%")
        volume_layout.addWidget(self.volume_label)
        general_layout.addLayout(volume_layout)
        
        # Behavior frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Behavior Frequency:"))
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(10, 100)
        self.freq_slider.setValue(self.config.get('settings.behavior_frequency', 50))
        self.freq_slider.valueChanged.connect(self._on_frequency_changed)
        freq_layout.addWidget(self.freq_slider)
        self.freq_label = QLabel(f"{self.freq_slider.value()}%")
        freq_layout.addWidget(self.freq_label)
        general_layout.addLayout(freq_layout)
        
        # Physics settings
        physics_group = QGroupBox("Physics Settings")
        physics_layout = QVBoxLayout(physics_group)

        # Gravity
        gravity_row_layout = QHBoxLayout()
        gravity_row_layout.addWidget(QLabel("Gravity (px/s²):"))
        self.gravity_spin = QSpinBox()
        self.gravity_spin.setRange(0, 2000)
        self.gravity_spin.setSingleStep(10)
        self.gravity_spin.setValue(self.config.get('settings.physics_gravity_acceleration', 980))
        self.gravity_spin.valueChanged.connect(lambda v: self.settings_changed.emit('physics_gravity_acceleration', v))
        self.gravity_spin.valueChanged.connect(lambda v: self.gravity_label.setText(f"{v}")) # Update label
        gravity_row_layout.addWidget(self.gravity_spin)
        self.gravity_label = QLabel(f"{self.gravity_spin.value()}") # Initial label value
        gravity_row_layout.addWidget(self.gravity_label)
        physics_layout.addLayout(gravity_row_layout)

        # Air Resistance
        air_res_row_layout = QHBoxLayout()
        air_res_row_layout.addWidget(QLabel("Air Resistance Factor (0.0-0.1):"))
        self.air_res_slider = QSlider(Qt.Horizontal)
        self.air_res_slider.setRange(0, 100) # Representing 0.0 to 0.1
        self.air_res_slider.setValue(int(self.config.get('settings.physics_air_resistance_factor', 0.001) * 1000))
        self.air_res_slider.valueChanged.connect(lambda v: self.settings_changed.emit('physics_air_resistance_factor', v / 1000.0))
        self.air_res_slider.valueChanged.connect(lambda v: self.air_res_label.setText(f"{v / 1000.0:.3f}")) # Update label
        air_res_row_layout.addWidget(self.air_res_slider)
        self.air_res_label = QLabel(f"{self.air_res_slider.value() / 1000.0:.3f}") # Initial label value
        air_res_row_layout.addWidget(self.air_res_label)
        physics_layout.addLayout(air_res_row_layout)

        # Bounce Coefficient
        bounce_coeff_row_layout = QHBoxLayout()
        bounce_coeff_row_layout.addWidget(QLabel("Bounce Coefficient (0.0-1.0):"))
        self.bounce_coeff_slider = QSlider(Qt.Horizontal)
        self.bounce_coeff_slider.setRange(0, 100) # Representing 0.0 to 1.0
        # Mengurangi nilai default bounce_coefficient menjadi 0.2 (dari 0.3)
        self.bounce_coeff_slider.setValue(int(self.config.get('settings.physics_bounce_coefficient', 0.2) * 100))
        self.bounce_coeff_slider.valueChanged.connect(lambda v: self.settings_changed.emit('physics_bounce_coefficient', v / 100.0))
        self.bounce_coeff_slider.valueChanged.connect(lambda v: self.bounce_coeff_label.setText(f"{v / 100.0:.2f}")) # Update label
        bounce_coeff_row_layout.addWidget(self.bounce_coeff_slider)
        self.bounce_coeff_label = QLabel(f"{self.bounce_coeff_slider.value() / 100.0:.2f}") # Initial label value
        bounce_coeff_row_layout.addWidget(self.bounce_coeff_label)
        physics_layout.addLayout(bounce_coeff_row_layout)

        # Throw Multiplier
        throw_mult_row_layout = QHBoxLayout()
        throw_mult_row_layout.addWidget(QLabel("Throw Multiplier (0.0-10.0):"))
        self.throw_mult_slider = QSlider(Qt.Horizontal)
        self.throw_mult_slider.setRange(0, 100) # Representing 0.0 to 10.0
        # Meningkatkan nilai default drag_throw_multiplier menjadi 6.0 (dari 4.0)
        self.throw_mult_slider.setValue(int(self.config.get('settings.physics_drag_throw_multiplier', 6.0) * 10))
        self.throw_mult_slider.valueChanged.connect(lambda v: self.settings_changed.emit('physics_drag_throw_multiplier', v / 10.0))
        self.throw_mult_slider.valueChanged.connect(lambda v: self.throw_mult_label.setText(f"{v / 10.0:.1f}")) # Update label
        throw_mult_row_layout.addWidget(self.throw_mult_slider)
        self.throw_mult_label = QLabel(f"{self.throw_mult_slider.value() / 10.0:.1f}") # Initial label value
        throw_mult_row_layout.addWidget(self.throw_mult_label)
        physics_layout.addLayout(throw_mult_row_layout)

        general_layout.addWidget(physics_group)
        
        # Checkboxes
        self.boundaries_check = QCheckBox("Keep pets within screen boundaries")
        self.boundaries_check.setChecked(self.config.get('settings.screen_boundaries', True))
        self.boundaries_check.toggled.connect(self._on_boundaries_changed)
        general_layout.addWidget(self.boundaries_check)
        
        self.autosave_check = QCheckBox("Auto-save settings")
        self.autosave_check.setChecked(self.config.get('settings.auto_save', True))
        self.autosave_check.toggled.connect(self._on_autosave_changed)
        general_layout.addWidget(self.autosave_check)
        
        self.debug_check = QCheckBox("Debug mode (show overlay)")
        self.debug_check.setChecked(self.config.get('settings.debug_mode', False))
        self.debug_check.toggled.connect(self._on_debug_changed)
        general_layout.addWidget(self.debug_check)

        self.show_stats_check = QCheckBox("Show Pet Stats Overlay")
        self.show_stats_check.setChecked(self.config.get('settings.show_stats', False))
        self.show_stats_check.toggled.connect(self._on_show_stats_changed)
        general_layout.addWidget(self.show_stats_check)
        
        layout.addWidget(general_group)
        
        # Configuration management
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)
        
        config_buttons_layout = QHBoxLayout()
        
        save_config_btn = QPushButton("Save Config")
        save_config_btn.clicked.connect(self._save_config_manual)
        config_buttons_layout.addWidget(save_config_btn)
        
        reload_config_btn = QPushButton("Reload Config")
        reload_config_btn.clicked.connect(self._reload_config)
        config_buttons_layout.addWidget(reload_config_btn)
        
        reset_config_btn = QPushButton("Reset to Defaults")
        reset_config_btn.clicked.connect(self._reset_config)
        reset_config_btn.setStyleSheet("QPushButton { background-color: #ffa500; }")
        config_buttons_layout.addWidget(reset_config_btn)
        
        config_layout.addLayout(config_buttons_layout)
        
        # Config file info
        config_info = QLabel(f"Config file: {self.config.config_file}")
        config_info.setWordWrap(True)
        config_layout.addWidget(config_info)
        
        layout.addWidget(config_group)
        
        # Spacer
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Settings")
    
    def _create_monitoring_tab(self) -> None:
        """Create monitoring and debugging tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance group
        perf_group = QGroupBox("Performance Monitor")
        perf_layout = QVBoxLayout(perf_group)
        
        self.perf_fps_label = QLabel("FPS: --")
        perf_layout.addWidget(self.perf_fps_label)
        
        self.perf_memory_label = QLabel("Memory: --")
        perf_layout.addWidget(self.perf_memory_label)
        
        self.perf_cache_label = QLabel("Sprite Cache: --")
        perf_layout.addWidget(self.perf_cache_label)
        
        layout.addWidget(perf_group)
        
        # Pet information group
        pets_group = QGroupBox("Active Pets")
        pets_layout = QVBoxLayout(pets_group)
        
        self.pets_info_text = QTextEdit()
        self.pets_info_text.setMaximumHeight(200)
        self.pets_info_text.setReadOnly(True)
        self.pets_info_text.setFont(QFont("Courier", 9))
        pets_layout.addWidget(self.pets_info_text)
        
        refresh_btn = QPushButton("Refresh Pet Info")
        refresh_btn.clicked.connect(self._refresh_pet_info)
        pets_layout.addWidget(refresh_btn)
        
        layout.addWidget(pets_group)
        
        # Actions group
        actions_group = QGroupBox("Debug Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        clear_cache_btn = QPushButton("Clear Sprite Cache")
        clear_cache_btn.clicked.connect(self._clear_sprite_cache)
        actions_layout.addWidget(clear_cache_btn)
        
        print_perf_btn = QPushButton("Print Performance to Console")
        print_perf_btn.clicked.connect(self._print_performance)
        actions_layout.addWidget(print_perf_btn)
        
        layout.addWidget(actions_group)
        
        # Spacer
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Monitoring")
    
    def _create_about_tab(self) -> None:
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Project info
        info_group = QGroupBox("About")
        info_layout = QVBoxLayout(info_group)
        
        title_label = QLabel(AppConstants.APP_NAME)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_layout.addWidget(title_label)
        
        version_label = QLabel(f"Version: {AppConstants.VERSION}")
        info_layout.addWidget(version_label)
        
        description_label = QLabel(
            "A desktop pet application inspired by Shimeji with TikTok Live integration capabilities.\n\n"
            "Features interactive desktop pets that can respond to TikTok Live chat in real-time."
        )
        description_label.setWordWrap(True)
        info_layout.addWidget(description_label)
        
        layout.addWidget(info_group)
        
        # Development status
        dev_group = QGroupBox("Development Status")
        dev_layout = QVBoxLayout(dev_group)
        
        status_text = QLabel(
            "✅ Phase 1 Step 1: Core Infrastructure (Complete)\n"
            "✅ Phase 1 Step 2: Control Panel Foundation (Complete)\n"
            "✅ Phase 1 Step 3: XML Parser & Animation System (Complete)\n"
            "🔄 Phase 1 Step 4: Desktop Boundaries & Physics (In Progress)"
        )
        status_text.setWordWrap(True)
        dev_layout.addWidget(status_text)
        
        layout.addWidget(dev_group)
        
        # Technical info
        tech_group = QGroupBox("Technical Information")
        tech_layout = QVBoxLayout(tech_group)
        
        tech_info = QLabel(
            f"Assets Directory: {AppConstants.ASSETS_DIR}\n"
            f"Config File: {self.config.config_file}\n"
            f"Target FPS: {AppConstants.TARGET_FPS}\n"
            f"Default Sprite Size: {AppConstants.DEFAULT_SPRITE_SIZE[0]}x{AppConstants.DEFAULT_SPRITE_SIZE[1]}"
        )
        tech_info.setWordWrap(True)
        tech_layout.addWidget(tech_info)
        
        layout.addWidget(tech_group)
        
        # Spacer
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "About")
    
    def _load_settings(self) -> None:
        """Load settings into UI components"""
        # Settings are loaded in individual widget creation
        # Update sliders and spinboxes with current config values
        self.volume_slider.setValue(self.config.get('settings.volume', 70))
        self.freq_slider.setValue(self.config.get('settings.behavior_frequency', 50))
        
        # Set values for physics sliders and update their labels
        gravity_val = self.config.get('settings.physics_gravity_acceleration', 980)
        self.gravity_spin.setValue(gravity_val)
        self.gravity_label.setText(f"{gravity_val}")

        air_res_val = self.config.get('settings.physics_air_resistance_factor', 0.001)
        self.air_res_slider.setValue(int(air_res_val * 1000))
        self.air_res_label.setText(f"{air_res_val:.3f}")

        bounce_coeff_val = self.config.get('settings.physics_bounce_coefficient', 0.2) # Updated default here
        self.bounce_coeff_slider.setValue(int(bounce_coeff_val * 100))
        self.bounce_coeff_label.setText(f"{bounce_coeff_val:.2f}")

        throw_mult_val = self.config.get('settings.physics_drag_throw_multiplier', 6.0) # Updated default here
        self.throw_mult_slider.setValue(int(throw_mult_val * 10))
        self.throw_mult_label.setText(f"{throw_mult_val:.1f}")

        self.boundaries_check.setChecked(self.config.get('settings.screen_boundaries', True))
        self.autosave_check.setChecked(self.config.get('settings.auto_save', True))
        self.debug_check.setChecked(self.config.get('settings.debug_mode', False))
        self.show_stats_check.setChecked(self.config.get('settings.show_stats', False))

        self._on_volume_changed(self.volume_slider.value())
        self._on_frequency_changed(self.freq_slider.value())
        
        saved_sprite = self.config.get('ui.selected_sprite')
        if saved_sprite and saved_sprite in self.sprite_packs:
            self.sprite_combo.setCurrentText(saved_sprite)

    def _on_sprite_changed(self, sprite_name: str) -> None:
        """Handle sprite selection change"""
        self.config.set('ui.selected_sprite', sprite_name)
        self.settings_changed.emit('selected_sprite', sprite_name)
    
    def _on_volume_changed(self, value: int) -> None:
        """Handle volume slider change"""
        self.config.set('settings.volume', value)
        self.volume_label.setText(f"{value}%")
        self.settings_changed.emit('volume', value)
    
    def _on_frequency_changed(self, value: int) -> None:
        """Handle frequency slider change"""
        self.config.set('settings.behavior_frequency', value)
        self.freq_label.setText(f"{value}%")
        self.settings_changed.emit('behavior_frequency', value)
    
    def _on_boundaries_changed(self, checked: bool) -> None:
        """Handle boundaries checkbox change"""
        self.config.set('settings.screen_boundaries', checked)
        self.settings_changed.emit('screen_boundaries', checked)
    
    def _on_autosave_changed(self, checked: bool) -> None:
        """Handle auto-save checkbox change"""
        self.config.set('settings.auto_save', checked)
        self.settings_changed.emit('auto_save', checked)
    
    def _on_debug_changed(self, checked: bool) -> None:
        """Handle debug mode checkbox change"""
        self.config.set('settings.debug_mode', checked)
        self.settings_changed.emit('debug_mode', checked)

    def _on_show_stats_changed(self, checked: bool) -> None:
        """Handle show stats checkbox change"""
        self.config.set('settings.show_stats', checked)
        self.settings_changed.emit('show_stats', checked)
    
    def _spawn_pet(self) -> None:
        """Spawn new pet(s)"""
        if not self.sprite_packs:
            return
        
        selected_sprite = self.sprite_combo.currentText()
        count = self.spawn_count_spin.value()
        
        for i in range(count):
            # Add offset for multiple pets
            offset_x = i * AppConstants.SPAWN_OFFSET if count > 1 else 0
            spawn_x = self.config.get('settings.spawn_x')
            spawn_y = self.config.get('settings.spawn_y')
            
            if spawn_x is None:
                spawn_x = self.pygame_window.screen_width // 2 + offset_x
            if spawn_y is None:
                spawn_y = self.pygame_window.screen_height - AppConstants.SCREEN_MARGIN
            
            pet_id = self.pygame_window.add_pet(selected_sprite, spawn_x, spawn_y)
            self.pet_spawned.emit(selected_sprite, pet_id)
        
        self.update_status()
    
    def _kill_all_pets(self) -> None:
        """Remove all pets"""
        count = self.pygame_window.clear_all_pets()
        self.update_status()
        print(f"Killed all {count} pets")
    
    def _save_config_manual(self) -> None:
        """Manually save configuration"""
        if self.config.save_config():
            print("Configuration saved successfully")
        else:
            print("Failed to save configuration")
    
    def _reload_config(self) -> None:
        """Reload configuration from file"""
        self.config.config = self.config.load_config()
        
        # Update UI with reloaded settings
        self.volume_slider.setValue(self.config.get('settings.volume', 70))
        self.freq_slider.setValue(self.config.get('settings.behavior_frequency', 50))
        self.boundaries_check.setChecked(self.config.get('settings.screen_boundaries', True))
        self.autosave_check.setChecked(self.config.get('settings.auto_save', True))
        self.debug_check.setChecked(self.config.get('settings.debug_mode', False))
        self.show_stats_check.setChecked(self.config.get('settings.show_stats', False))

        # Reload values for physics sliders and update their labels
        gravity_val = self.config.get('settings.physics_gravity_acceleration', 980)
        self.gravity_spin.setValue(gravity_val)
        self.gravity_label.setText(f"{gravity_val}")

        air_res_val = self.config.get('settings.physics_air_resistance_factor', 0.001)
        self.air_res_slider.setValue(int(air_res_val * 1000))
        self.air_res_label.setText(f"{air_res_val:.3f}")

        bounce_coeff_val = self.config.get('settings.physics_bounce_coefficient', 0.2) # Updated default here
        self.bounce_coeff_slider.setValue(int(bounce_coeff_val * 100))
        self.bounce_coeff_label.setText(f"{bounce_coeff_val:.2f}")

        throw_mult_val = self.config.get('settings.physics_drag_throw_multiplier', 6.0) # Updated default here
        self.throw_mult_slider.setValue(int(throw_mult_val * 10))
        self.throw_mult_label.setText(f"{throw_mult_val:.1f}")
        
        # Update labels
        self._on_volume_changed(self.volume_slider.value())
        self._on_frequency_changed(self.freq_slider.value())
        
        saved_sprite = self.config.get('ui.selected_sprite')
        if saved_sprite and saved_sprite in self.sprite_packs:
            self.sprite_combo.setCurrentText(saved_sprite)
        
        print("Configuration reloaded")
    
    def _reset_config(self) -> None:
        """Reset configuration to defaults"""
        self.config.reset_to_defaults()
        self._reload_config()
        print("Configuration reset to defaults")
    
    def _clear_sprite_cache(self) -> None:
        """Clear sprite cache"""
        from sprite_loader import get_sprite_loader
        get_sprite_loader().clear_cache()
        print("Sprite cache cleared")
    
    def _print_performance(self) -> None:
        """Print performance info to console"""
        self.pygame_window._print_performance_info()
    
    def _refresh_pet_info(self) -> None:
        """Refresh pet information display"""
        pets_info = self.pygame_window.get_pets_info()
        
        if not pets_info:
            self.pets_info_text.setText("No active pets")
            return
        
        info_text = ""
        for pet_info in pets_info:
            info_text += f"Pet ID: {pet_info['pet_id']}\n"
            info_text += f"  Sprite: {pet_info['sprite_name']}\n"
            info_text += f"  Position: ({pet_info['position'][0]:.0f}, {pet_info['position'][1]:.0f})\n"
            info_text += f"  Velocity: ({pet_info['velocity'][0]:.0f}, {pet_info['velocity'][1]:.0f})\n" # Added velocity
            info_text += f"  State: {pet_info['state']}\n"
            info_text += f"  Health: {pet_info['stats']['health']:.0f}\n"
            info_text += f"  Happiness: {pet_info['stats']['happiness']:.0f}\n"
            info_text += f"  Energy: {pet_info['stats']['energy']:.0f}\n"
            info_text += f"  Interactions: {pet_info['stats']['interactions']}\n"
            info_text += "-" * 30 + "\n"
        
        self.pets_info_text.setText(info_text)
    
    def update_status(self) -> None:
        """Update status displays"""
        # Update pet count
        pet_count = len(self.pygame_window.pets)
        self.pet_count_label.setText(f"Active pets: {pet_count}")
        
        # Update performance info
        perf_info = self.pygame_window.get_performance_info()
        self.performance_label.setText(f"FPS: {perf_info['fps']:.1f}")
        
        # Update monitoring tab if it's currently visible
        if self.tab_widget.currentIndex() == 2:  # Monitoring tab
            self.perf_fps_label.setText(f"FPS: {perf_info['fps']:.1f}")
            self.perf_memory_label.setText(f"Memory: {perf_info['memory_usage_mb']:.1f}MB")
            self.perf_cache_label.setText(f"Sprite Cache: {perf_info['sprite_cache']['cached_sprites']} sprites")
            self._refresh_pet_info() # Refresh pet info in monitoring tab
    
    def closeEvent(self, event) -> None:
        """Handle window close event"""
        # Save window position
        pos = self.pos()
        self.config.set('ui.control_panel_x', pos.x())
        self.config.set('ui.control_panel_y', pos.y())
        
        # Stop update timer
        self.update_timer.stop()
        
        # Save final config
        self.config.save_config()
        
        print("Control panel closed")
        event.accept()
