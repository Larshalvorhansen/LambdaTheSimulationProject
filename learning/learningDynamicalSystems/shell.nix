{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.numpy
    python3Packages.scipy
    python3Packages.matplotlib
  ];

  shellHook = ''
    echo "Python environment ready!"
    echo "Available packages:"
    echo "  - numpy"
    echo "  - scipy"
    echo "  - matplotlib"
    python --version
  '';
}
