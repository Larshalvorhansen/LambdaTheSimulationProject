{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = [ pkgs.gcc pkgs.pkg-config pkgs.raylib ];

  shellHook = ''
    echo "🛠  Nix shell ready."
    echo "   Build:   make"
    echo "   Run:     ./econpatch.c"
  '';
}
