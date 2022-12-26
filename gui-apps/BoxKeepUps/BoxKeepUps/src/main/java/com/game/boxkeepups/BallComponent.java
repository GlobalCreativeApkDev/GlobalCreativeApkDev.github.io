package com.game.boxkeepups;

import com.almasb.fxgl.entity.component.Component;
import com.almasb.fxgl.physics.PhysicsComponent;
import javafx.geometry.Point2D;

import static com.almasb.fxgl.dsl.FXGLForKtKt.getAppHeight;
import static com.almasb.fxgl.dsl.FXGLForKtKt.getAppWidth;
import static com.almasb.fxgl.dsl.FXGLForKtKt.getGameScene;
import static java.lang.Math.abs;
import static java.lang.Math.signum;

/**
 * The code in this file is inspired by the following source.
 * <a href="https://github.com/AlmasB/FXGLGames/tree/master/Pong">...</a>
 * */

public class BallComponent extends Component {
    // The physics component
    protected PhysicsComponent physics;

    // Actions of the ball on update

    @Override
    public void onUpdate(double tpf) {
        limitVelocity();
        checkOffScreen();
    }

    private void limitVelocity() {
        // Ensuring that the ball does not move too slow vertically
        if (abs(physics.getVelocityY()) < 6 * 60) {
            physics.setVelocityY(signum(physics.getVelocityY()) * 6 * 60);
        }
    }

    private void checkOffScreen() {
        if (getEntity().getBoundingBoxComponent().isOutside(getGameScene().getViewport().getVisibleArea())) {
            physics.overwritePosition(new Point2D(
                    getAppWidth() / 2,
                    getAppHeight() / 2
            ));
        }
    }
}
