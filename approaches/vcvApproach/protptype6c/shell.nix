{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  packages = [ pkgs.gcc pkgs.pkg-config pkgs.portaudio ];

  shellHook = ''
    echo "✅ Dev shell ready. Build with: make"
    echo "▶️  Then run: ./tiny_rack -d 6"
  '';
}
