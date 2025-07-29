#!/usr/bin/env python3
"""
utils/xml_parser.py - XML configuration parser

Handles parsing of Shimeji XML configuration files (actions.xml and behaviors.xml)
with proper error handling and validation.
"""

import xml.etree.ElementTree as ET
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from config import AppConstants


@dataclass
class PoseData:
    """Data structure for animation pose information"""
    image: str
    image_anchor: tuple
    velocity: tuple
    duration: int
    sound: Optional[str] = None
    volume: Optional[int] = None


@dataclass
class AnimationData:
    """Data structure for animation sequence"""
    poses: List[PoseData]
    condition: Optional[str] = None


@dataclass
class ActionData:
    """Data structure for action configuration"""
    name: str
    action_type: str
    animations: List[AnimationData]
    border_type: Optional[str] = None


@dataclass
class BehaviorData:
    """Data structure for behavior configuration"""
    name: str
    frequency: int
    hidden: bool = False
    condition: Optional[str] = None
    next_behaviors: Optional[List[str]] = None


class XMLParser:
    """XML parser for Shimeji configuration files"""
    
    def __init__(self):
        self.actions: Dict[str, ActionData] = {}
        self.behaviors: Dict[str, BehaviorData] = {}
    
    def parse_sprite_pack(self, sprite_name: str) -> bool:
        """Parse both actions.xml and behaviors.xml for a sprite pack"""
        try:
            actions_path = AppConstants.get_xml_path(sprite_name, AppConstants.ACTIONS_XML)
            behaviors_path = AppConstants.get_xml_path(sprite_name, AppConstants.BEHAVIORS_XML)
            
            actions_success = self.parse_actions(actions_path)
            behaviors_success = self.parse_behaviors(behaviors_path)
            
            return actions_success and behaviors_success
            
        except Exception as e:
            print(f"Error parsing sprite pack {sprite_name}: {e}")
            return False
    
    def parse_actions(self, xml_path: str) -> bool:
        """Parse actions.xml file"""
        try:
            if not os.path.exists(xml_path):
                print(f"Actions XML not found: {xml_path}")
                return False
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Find ActionList element
            action_list = root.find('.//{http://www.group-finity.com/Mascot}ActionList')
            if action_list is None:
                print(f"ActionList not found in {xml_path}")
                return False
            
            # Parse each Action
            for action_elem in action_list.findall('.//{http://www.group-finity.com/Mascot}Action'):
                action_data = self._parse_action_element(action_elem)
                if action_data:
                    self.actions[action_data.name] = action_data
            
            print(f"Parsed {len(self.actions)} actions from {xml_path}")
            return True
            
        except ET.ParseError as e:
            print(f"XML parse error in {xml_path}: {e}")
            return False
        except Exception as e:
            print(f"Error parsing actions from {xml_path}: {e}")
            return False
    
    def parse_behaviors(self, xml_path: str) -> bool:
        """Parse behaviors.xml file"""
        try:
            if not os.path.exists(xml_path):
                print(f"Behaviors XML not found: {xml_path}")
                return False
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Find BehaviorList element
            behavior_list = root.find('.//{http://www.group-finity.com/Mascot}BehaviorList')
            if behavior_list is None:
                print(f"BehaviorList not found in {xml_path}")
                return False
            
            # Parse each Behavior
            for behavior_elem in behavior_list.findall('.//{http://www.group-finity.com/Mascot}Behavior'):
                behavior_data = self._parse_behavior_element(behavior_elem)
                if behavior_data:
                    self.behaviors[behavior_data.name] = behavior_data
            
            print(f"Parsed {len(self.behaviors)} behaviors from {xml_path}")
            return True
            
        except ET.ParseError as e:
            print(f"XML parse error in {xml_path}: {e}")
            return False
        except Exception as e:
            print(f"Error parsing behaviors from {xml_path}: {e}")
            return False
    
    def _parse_action_element(self, action_elem) -> Optional[ActionData]:
        """Parse a single Action element"""
        try:
            name = action_elem.get('Name')
            action_type = action_elem.get('Type', 'Stay')
            border_type = action_elem.get('BorderType')
            
            if not name:
                return None
            
            animations = []
            
            # Parse Animation elements
            for anim_elem in action_elem.findall('.//{http://www.group-finity.com/Mascot}Animation'):
                animation_data = self._parse_animation_element(anim_elem)
                if animation_data:
                    animations.append(animation_data)
            
            return ActionData(
                name=name,
                action_type=action_type,
                border_type=border_type,
                animations=animations
            )
            
        except Exception as e:
            print(f"Error parsing action element: {e}")
            return None
    
    def _parse_animation_element(self, anim_elem) -> Optional[AnimationData]:
        """Parse a single Animation element"""
        try:
            condition = anim_elem.get('Condition')
            poses = []
            
            # Parse Pose elements
            for pose_elem in anim_elem.findall('.//{http://www.group-finity.com/Mascot}Pose'):
                pose_data = self._parse_pose_element(pose_elem)
                if pose_data:
                    poses.append(pose_data)
            
            return AnimationData(poses=poses, condition=condition)
            
        except Exception as e:
            print(f"Error parsing animation element: {e}")
            return None
    
    def _parse_pose_element(self, pose_elem) -> Optional[PoseData]:
        """Parse a single Pose element"""
        try:
            image = pose_elem.get('Image', '')
            image_anchor_str = pose_elem.get('ImageAnchor', '64,128')
            velocity_str = pose_elem.get('Velocity', '0,0')
            duration = int(pose_elem.get('Duration', 1))
            sound = pose_elem.get('Sound')
            volume = pose_elem.get('Volume')
            
            # Parse comma-separated values
            image_anchor = tuple(map(int, image_anchor_str.split(',')))
            velocity = tuple(map(int, velocity_str.split(',')))
            
            if volume is not None:
                volume = int(volume)
            
            return PoseData(
                image=image.lstrip('/'),  # Remove leading slash
                image_anchor=image_anchor,
                velocity=velocity,
                duration=duration,
                sound=sound.lstrip('/') if sound else None,
                volume=volume
            )
            
        except (ValueError, IndexError) as e:
            print(f"Error parsing pose element: {e}")
            return None
    
    def _parse_behavior_element(self, behavior_elem) -> Optional[BehaviorData]:
        """Parse a single Behavior element"""
        try:
            name = behavior_elem.get('Name')
            frequency = int(behavior_elem.get('Frequency', 0))
            hidden = behavior_elem.get('Hidden', 'false').lower() == 'true'
            condition = behavior_elem.get('Condition')
            
            if not name:
                return None
            
            # Parse NextBehaviorList if present
            next_behaviors = []
            next_behavior_list = behavior_elem.find('.//{http://www.group-finity.com/Mascot}NextBehaviorList')
            if next_behavior_list is not None:
                for behavior_ref in next_behavior_list.findall('.//{http://www.group-finity.com/Mascot}BehaviorReference'):
                    ref_name = behavior_ref.get('Name')
                    if ref_name:
                        next_behaviors.append(ref_name)
            
            return BehaviorData(
                name=name,
                frequency=frequency,
                hidden=hidden,
                condition=condition,
                next_behaviors=next_behaviors if next_behaviors else None
            )
            
        except (ValueError, TypeError) as e:
            print(f"Error parsing behavior element: {e}")
            return None
    
    def get_action(self, name: str) -> Optional[ActionData]:
        """Get action data by name"""
        return self.actions.get(name)
    
    def get_behavior(self, name: str) -> Optional[BehaviorData]:
        """Get behavior data by name"""
        return self.behaviors.get(name)
    
    def get_all_actions(self) -> Dict[str, ActionData]:
        """Get all parsed actions"""
        return self.actions.copy()
    
    def get_all_behaviors(self) -> Dict[str, BehaviorData]:
        """Get all parsed behaviors"""
        return self.behaviors.copy()
    
    def clear(self) -> None:
        """Clear all parsed data"""
        self.actions.clear()
        self.behaviors.clear()
    
    def validate_sprite_xml(self, sprite_name: str) -> bool:
        """Validate XML files exist and are parseable"""
        actions_path = AppConstants.get_xml_path(sprite_name, AppConstants.ACTIONS_XML)
        behaviors_path = AppConstants.get_xml_path(sprite_name, AppConstants.BEHAVIORS_XML)
        
        # Check if files exist
        if not os.path.exists(actions_path):
            print(f"Missing actions.xml for sprite pack: {sprite_name}")
            return False
        
        if not os.path.exists(behaviors_path):
            print(f"Missing behaviors.xml for sprite pack: {sprite_name}")
            return False
        
        # Try parsing both files
        temp_parser = XMLParser()
        actions_valid = temp_parser.parse_actions(actions_path)
        behaviors_valid = temp_parser.parse_behaviors(behaviors_path)
        
        return actions_valid and behaviors_valid
