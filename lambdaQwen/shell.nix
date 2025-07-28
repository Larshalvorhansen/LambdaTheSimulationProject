# shell.nix
{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.numpy
    python3Packages.pandas # Useful for data analysis if needed later
    python3Packages.matplotlib # For potential plotting
  ];

  shellHook = ''
    echo "Entering LambdaSim development environment"
    # You can add alias or environment variable settings here if needed
  '';
}
