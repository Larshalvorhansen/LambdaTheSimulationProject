{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  name = "company-worker-tk";

  # python3Full includes Tkinter (tk) out of the box
  packages = with pkgs; [ python3Full ];

  shellHook = ''
    echo "✅ Tkinter ready. Run:  python app.py"
  '';
}
