package com.game.boxkeepups;

import com.almasb.fxgl.dsl.FXGL;
import com.almasb.fxgl.entity.component.Component;
import com.almasb.fxgl.physics.PhysicsComponent;

/**
 * The code in this file is inspired by the following source.
 * <a href="https://github.com/AlmasB/FXGLGames/tree/master/Pong">...</a>
 * */

public class BoxComponent extends Component {
    // Box speed
    private static final double BOX_SPEED = 450;

    // Physics component of the box
    protected PhysicsComponent physics;

    public void left() {
        if (entity.getRightX() >= BOX_SPEED / 60)
            physics.setVelocityX(-BOX_SPEED);
        else
            stop();
    }

    public void right() {
        if (entity.getRightX() <= FXGL.getAppWidth() - (BOX_SPEED / 60))
            physics.setVelocityX(BOX_SPEED);
        else
            stop();
    }

    public void stop() {
        physics.setLinearVelocity(0, 0);
    }
}
