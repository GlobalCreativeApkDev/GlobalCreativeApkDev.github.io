package com.game.fantasyplanetadventure.common.minigames;

import java.io.Serializable;

public class BoxEatsPlantsBoard implements Serializable, Cloneable {
    /**
     * This class contains attributes of a board in the game "Box Eats Plants".
     * @author GlobalCreativeApkDev
     * */

    // Class attributes
    private final int BOARD_WIDTH = 10;
    private final int BOARD_HEIGHT = 10;
    private BoxEatsPlantsTile[][] tiles;

    public BoxEatsPlantsBoard() {
        tiles = new BoxEatsPlantsTile[BOARD_HEIGHT][BOARD_WIDTH];
        for (int i = 0; i < BOARD_HEIGHT; i++) {
            BoxEatsPlantsTile[] newList = new BoxEatsPlantsTile[BOARD_WIDTH];
            for (int j = 0; j < BOARD_WIDTH; j++) {
                newList[j] = new BoxEatsPlantsTile();
            }

            tiles[i] = newList;
        }
    }
}
