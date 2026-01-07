{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "salmon-abm";
  
  buildInputs = with pkgs; [
    (python3.withPackages (ps: with ps; [
      numpy
      matplotlib
    ]))
  ];

  shellHook = ''
    echo "🐟 Salmon ABM environment loaded"
    echo "Python: $(python --version)"
    echo ""
    echo "Available packages:"
    echo "  - numpy"
    echo "  - matplotlib (with animation support)"
    echo ""
    echo "Run: python duopoly_animation.py"
  '';
}
