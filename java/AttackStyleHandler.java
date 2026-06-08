package net.runelite.client.plugins.asd;

import com.google.inject.Singleton;
import net.runelite.api.Client;
import net.runelite.api.EnumID;
import net.runelite.api.ParamID;
import net.runelite.api.StructComposition;
import javax.inject.Inject;
import java.util.HashMap;
import java.util.Map;

@Singleton
public class AttackStyleHandler {

    @Inject
    private Client client;

    private enum AttackStyle {
        ACCURATE,
        AGGRESSIVE,
        DEFENSIVE,
        CASTING,
        DEFENSIVE_CASTING,
        OTHER;

        public String getName() {
            switch (this) {
                case ACCURATE:
                    return "Accurate";
                case AGGRESSIVE:
                    return "Aggressive";
                case DEFENSIVE:
                    return "Defensive";
                case CASTING:
                    return "Casting";
                case DEFENSIVE_CASTING:
                    return "Defensive Casting";
                default:
                    return "Other";
            }
        }
    }

    public Map<String, Object> getCurrentAttackStyle() {
        int styleIndex = client.getVarpValue(43);           // COM_MODE
        int weaponCategory = client.getVarbitValue(357);    // COMBAT_WEAPON_CATEGORY
        int castingMode = client.getVarbitValue(2668);      // AUTOCAST_DEFMODE

        AttackStyle[] styles = getWeaponTypeStyles(weaponCategory);

        AttackStyle style = AttackStyle.OTHER;
        if (styleIndex < styles.length) {
            if (styleIndex == 4) { // staves use 5th style + defensive flag
                styleIndex += castingMode;
            }
            if (styles[styleIndex] != null) {
                style = styles[styleIndex];
            }
        }

        Map<String, Object> data = new HashMap<>();
        data.put("style", style.name());
        data.put("name", style.getName());
        data.put("styleIndex", styleIndex);
        data.put("weaponCategory", weaponCategory);
        data.put("defensiveCasting", castingMode == 1);
        return data;
    }

    private AttackStyle[] getWeaponTypeStyles(int weaponType) {
        int weaponStyleEnum = client.getEnum(EnumID.WEAPON_STYLES).getIntValue(weaponType);
        if (weaponStyleEnum == -1) {
            if (weaponType == 22) { // Blue moon spear
                return new AttackStyle[]{AttackStyle.ACCURATE, AttackStyle.AGGRESSIVE, null, AttackStyle.DEFENSIVE, AttackStyle.CASTING, AttackStyle.DEFENSIVE_CASTING};
            }
            if (weaponType == 30) { // Partisan
                return new AttackStyle[]{AttackStyle.ACCURATE, AttackStyle.AGGRESSIVE, AttackStyle.AGGRESSIVE, AttackStyle.DEFENSIVE};
            }
            return new AttackStyle[0];
        }

        int[] weaponStyleStructs = client.getEnum(weaponStyleEnum).getIntVals();
        AttackStyle[] styles = new AttackStyle[weaponStyleStructs.length];
        int i = 0;
        for (int structId : weaponStyleStructs) {
            StructComposition struct = client.getStructComposition(structId);
            String name = struct.getStringValue(ParamID.ATTACK_STYLE_NAME);

            AttackStyle as;
            try {
                as = AttackStyle.valueOf(name.toUpperCase());
            } catch (IllegalArgumentException e) {
                as = AttackStyle.OTHER;
            }

            if (as == AttackStyle.OTHER) {
                i++;
                continue;
            }
            if (i == 5 && as == AttackStyle.DEFENSIVE) {
                as = AttackStyle.DEFENSIVE_CASTING;
            }
            styles[i++] = as;
        }
        return styles;
    }
}