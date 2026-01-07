using Gtk

global blocks 

function main()
    global blocks = Block[] 
    win = GtkWindow("Movable Blocks GUI", 800, 600)

    canvas = GtkCanvas()
    push!(win, canvas)

    # Data structure to store blocks
    blocks = Block[]

    # Event connections
    canvas.signal_connect("draw", draw_blocks(canvas, blocks))
    canvas.signal_connect("button-press-event", on_mouse_down(canvas, blocks))
    canvas.signal_connect("button-release-event", on_mouse_up(blocks))
    canvas.signal_connect("motion-notify-event", on_mouse_move(canvas, blocks))
    
    win.set_events(Gdk.EventMask.ALL_EVENTS_MASK) # Enable events

    showall(win)
end

struct Block
    x::Int
    y::Int
    width::Int
    height::Int
    input_points::Vector{Tuple{Int, Int}}
    output_points::Vector{Tuple{Int, Int}}
    active::Bool  # Track if the block is selected
end

function draw_block(cr, block::Block)
    set_source_rgb(cr, 0.5, 0.5, 0.5) # Gray color
    if block.active
        set_source_rgb(cr, 1.0, 0.0, 0.0) # Highlight active block in red
    end
    rectangle(cr, block.x, block.y, block.width, block.height)
    fill(cr)
end

function draw_wire(cr, start_point, end_point)
    set_source_rgb(cr, 0, 0, 0) # Black color
    move_to(cr, start_point...)
    line_to(cr, end_point...)
    stroke(cr)
end

function draw_blocks(canvas, blocks)
    return function(canvas, cr)
        for block in blocks
            draw_block(cr, block)
        end
    end
end

function on_mouse_down(canvas, blocks)
    return function(widget, event)
        x, y = event.x, event.y

        # Find clicked block
        for (index, block) in enumerate(blocks)
            if x >= block.x && x <= block.x + block.width &&
               y >= block.y && y <= block.y + block.height
                blocks[index].active = true
                canvas.queue_draw()  # Redraw
                break
            end
        end
    end
end

function on_mouse_move(canvas, blocks)
    return function(widget, event)
        x, y = event.x, event.y

        for block in blocks
            if block.active
                block.x = x - block.width / 2  # Adjust for centering
                block.y = y - block.height / 2
                canvas.queue_draw()  # Redraw
                break
            end
        end
    end
end

function on_mouse_up(blocks)
    return function(widget, event)
        for block in blocks
            block.active = false
        end
    end
end

# Initialize some blocks 
push!(blocks, Block(100, 50, 50, 50, [], []))
push!(blocks, Block(300, 150, 80, 30, [], []))

main()
