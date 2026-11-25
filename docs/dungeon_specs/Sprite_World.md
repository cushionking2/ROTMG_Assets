# Sprite World

Source files: Sprite World - the RotMG Wiki _ RealmEye.com.html; Sprite World Guide - the RotMG Wiki _ RealmEye.com.html

## Overview
- Portal / how to enter: The portal has a chance to drop from Sprite Beast and Sprite Child. It always drops from Celestial Sprite and Cosmic Sprite. These enemies live in the Sprite Forest. The Sprite World Key costs 100 in the Nexus.
- Theme and setting: A dimensional plane among the stars. Colorful platforms float in a starry void. The sprites are manifestations of elemental energy. Five elements exist: Darkness, Fire, Ice, Magic, Nature.
- Party size, difficulty, level range: The page calls it a low to medium-level dungeon for level 20 unmaxed characters. The guide lists "Recommended: Level 20". Enemies are weak. The boss can be dangerous. The wiki says it is the most commonly run dungeon (June 2020 data).
- Time or wave limits, if any: No time limit is given. Portals open at random around players. Each portal spawns regular or Greater Sprites, then disappears.

## Layout and map logic
- Overall structure (rooms, corridors, open cave, grid, linear): Platforms ("rooms") float in a void and join by walkways. There are no proper walls. Players cannot walk across the void. Players can teleport freely because no walls block rendering. Music: Arc Sancts.
- Room sizes and counts, if the guide gives them: There are always 5 rooms between the start room and Limon's room, not counting either. The boss platform is square, black tiles, bordered by 4 conveyor belts. No other sizes are given.
- Special mechanics (keys, doors, waves, hazards, puzzles, destructible walls):
  - Multicolored conveyor belts push players in their direction.
  - Many rooms show pixel art (visible on the minimap). A few platforms reference game enemies and items (Goblin Mage, Pirate, Flayer, Honey Scepter, Craig the Intern, Wizard, Ent Ancient, Art sprite, Sprite God).
  - Almost all rooms hold destructible Sprite Tree obstacles (HP 100, count toward Structure Kills).
  - If a player attacks Limon before killing any sprite, she spawns 5-6 portals with many regular and Greater Sprites. If no sprite died before activation, she follows players and stays vulnerable until attacked.
- Order of progress (rooms, minibosses, boss): Start room, 5 rooms, Limon's room. Native Sprite Gods act as tough regular enemies.
  - Limon phase 1: she cycles 3-way orange laser bursts (1 shot per burst, +1 each burst, reset after 5), dashing with paired lasers, and an armored 2-armed clockwise spiral. With no target she fires rings of orange waves.
  - Limon phase 2: she turns Invulnerable, then takes a Magic, Ice, Nature or Darkness form. Each form has its own pattern and arena shots.
  - Limon phase 3 (at 40% HP): she returns to her original form. The platform becomes a double ring of conveyor belts (outer clockwise, inner counterclockwise). Limon Elements fire pink bolt streams along the diagonals, making 4 quadrants. She moves between quadrants and fires wavy orange pairs, a collapsing ring of fire bolts, and an aimed armor-piercing rainbow blast.
  - On death, the Limon Elements deactivate and the arena becomes a plain black square.

## Enemies
| Name | Role (regular / miniboss / boss) | Key attacks or behavior | Notes |
|---|---|---|---|
| Native Darkness Sprite | regular | Unique shot pattern; fast, dies in a few hits | Small and weak |
| Native Fire Sprite | regular | Same as above | |
| Native Ice Sprite | regular | Ice variants consistently inflict Slowed | |
| Native Magic Sprite | regular | Same as above | Listed as a drop source |
| Native Nature Sprite | regular | Same as above | Listed as a drop source |
| Native Greater Darkness Sprite | regular | More HP, more dangerous attacks; slow | |
| Native Greater Fire Sprite | regular | Same as above | |
| Native Greater Ice Sprite | regular | Same as above; Slowed shots | |
| Native Greater Magic Sprite | regular | Same as above | |
| Native Greater Nature Sprite | regular | Same as above | All Greater Sprites are drop sources |
| Native Sprite God | regular (strong) | Five colored variants; huge damage in some forms; deadly at close range | May drop Potions of Attack at a higher rate than regular Sprite Gods |
| Craig the Intern | regular | Not described | Listed in enemy section |
| Limon the Sprite Goddess | boss | See phases above | Has colored forms; guide names 4 (Magic, Ice, Nature, Darkness) |
| Limon Element | boss helper | 4 sit in the arena corners; make pink shot borders and diagonal streams | |
| Sprite Tree | environment | Destructible obstacle, HP 100 | |
| Sprite Child, Sprite Beast, Celestial Sprite, Cosmic Sprite | outside enemies (portal droppers) | Found in Sprite Forest | Sprite Children spawn from Sprite Gods |

## Tiles and objects to find as sprites
- Floor tiles: Colored platform tiles. Black tiles in the boss room. Colored conveyor belt tiles.
- Wall tiles: None. The dungeon has no proper walls. A void of stars surrounds the platforms.
- Hazards and props: Sprite Trees. Limon Elements. Conveyor belts. Arena shots (pink, green beams, rainbow stars, slowing shots).
- Other objects (chests, portals, doors, keys): Random spawn portals. Sprite World portal and key. Reward drops from Limon.

## Loot
- Boss drops Potions of Dexterity (at least two, to two players) and rarely a Potion of Defense. It is the main Dexterity source.
- Untiered items: Sprite Wand, Staff of Extreme Prejudice, Cloak of the Planewalker, Mace of the Celestial Forest. Feed powers per guide: 750 (Cloak), 600 (Staff), 750 (Mace), 150 (Sprite Wand).
- Rare Sprite Star Pet skin. Tarot Card Pack source. Native Sprite Gods may drop Potions of Attack.
- Completion is needed for the King of the Mountains, Hero of the Nexus and Realm of the Mad God fame bonuses. The page shows "22-30" under Dust Drops, with other numbers lost.

## Sprite search hints
- Words to search in `Objects.xml` and `GroundTypes.xml`: Sprite, Native, Greater, Limon, Limon Element, Sprite God, Sprite Tree, Craig, Conveyor, Sprite World, Star, Celestial, Cosmic, Rainbow, Dimension.

## Gaps
- Exact platform sizes and the pixel-art platform layouts.
- HP and defense of all enemies and Limon.
- Exact HP thresholds for phase 2 and its form order.
- Item names in the drop tables were images and are lost. Some drop-to-enemy links are unclear.
- Names of the ground tiles and conveyor object ids.
- Number of portals per room and spawn timing.
