# shell.nix
{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  packages = [
    # python3Full includes Tkinter support out of the box
    (pkgs.python3Full.withPackages (_: [ ]))
  ];

  # nice-to-haves
  shellHook = ''
    echo "Python: $(python --version)"
    python -c "import tkinter as tk; print('Tkinter OK:', bool(tk.TkVersion))"
  '';
}
