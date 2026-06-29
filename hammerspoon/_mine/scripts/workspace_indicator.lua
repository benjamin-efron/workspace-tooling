local M = {}

local BADGE_W    = 72
local BADGE_H    = 72
local CORNER_R   = 14
local TEXT_SIZE  = 36
local BG_COLOR   = {red = 0.08, green = 0.08, blue = 0.08, alpha = 0.88}
local TEXT_COLOR = {red = 1.0,  green = 1.0,  blue = 1.0,  alpha = 1.0}
local DURATION   = 0.5  -- seconds

local activeCanvas = nil
local activeTimer  = nil

-- Show a brief workspace badge on the focused screen.
-- label is the workspace name/number from AeroSpace.
function M.show(label)
    if activeTimer  then activeTimer:stop();   activeTimer  = nil end
    if activeCanvas then activeCanvas:delete(); activeCanvas = nil end

    local screen = (hs.window.focusedWindow() and hs.window.focusedWindow():screen())
                or hs.screen.mainScreen()
    local f = screen:frame()

    local x = f.x + (f.w - BADGE_W) / 2
    local y = f.y + f.h - BADGE_H - 40

    local canvas = hs.canvas.new({x = x, y = y, w = BADGE_W, h = BADGE_H})
    canvas[1] = {
        type              = "rectangle",
        action            = "fill",
        fillColor         = BG_COLOR,
        roundedRectRadii  = {xRadius = CORNER_R, yRadius = CORNER_R},
        frame             = {x = 0, y = 0, w = BADGE_W, h = BADGE_H},
    }
    canvas[2] = {
        type          = "text",
        text          = tostring(label),
        textColor     = TEXT_COLOR,
        textSize      = TEXT_SIZE,
        textAlignment = "center",
        frame         = {x = 0, y = (BADGE_H - TEXT_SIZE) / 2 - 2, w = BADGE_W, h = TEXT_SIZE + 8},
    }

    canvas:show()
    activeCanvas = canvas
    activeTimer  = hs.timer.doAfter(DURATION, function()
        canvas:delete()
        activeCanvas = nil
        activeTimer  = nil
    end)
end

return M
