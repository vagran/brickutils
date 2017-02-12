# brickutils
LEGO bricks management utilities

Currently supports bricks colors resetting to "any" for [BrickOwl](http://brickowl.com) wishlists.

Use command: `./brickutil.py wishlist-remove-colors --wishlist-id <your-wishlist-id> --dst-wishlist-id <your-destination-wishlist-id>`

Wishlist ID can be obtained by this command: `./brickutil.py list-wishlists`.

Configuration file with your BrickOwl API key should be avaialble in `$HOME/.brickutil.conf`. Use `config-example` file as template.
