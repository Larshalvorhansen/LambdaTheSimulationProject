{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python and core dependencies
    python311
    python311Packages.pip
    python311Packages.virtualenv

    # PyQt6 and Qt dependencies
    python311Packages.pyqt6
    python311Packages.pyqt6-sip
    qt6.full

    # Scientific computing libraries
    python311Packages.numpy
    python311Packages.scipy
    python311Packages.pandas
    python311Packages.sympy

    # Plotting and visualization
    python311Packages.pyqtgraph
    python311Packages.matplotlib

    # Additional useful tools
    python311Packages.networkx # For graph algorithms (execution order)
    python311Packages.h5py # For HDF5 data storage

    # Development tools
    python311Packages.pytest
    python311Packages.black
    python311Packages.pylint
    python311Packages.ipython
  ];

  shellHook = ''
    echo "System Dynamics Node Editor - Development Environment"
    echo "======================================================"
    echo "Python: $(python --version)"
    echo "PyQt6 available"
    echo ""
    echo "To run the application:"
    echo "  python main.py"
    echo ""
    echo "Development tools available:"
    echo "  - pytest (testing)"
    echo "  - black (code formatting)"
    echo "  - pylint (linting)"
    echo "  - ipython (interactive shell)"
    echo ""

    # Set up Qt platform
    export QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.qt6.qtbase}/lib/qt-6/plugins"
    export QT_PLUGIN_PATH="${pkgs.qt6.qtbase}/lib/qt-6/plugins"

    # Detect platform and set appropriate Qt backend
    if [[ "$OSTYPE" == "darwin"* ]]; then
      export QT_QPA_PLATFORM="cocoa"
      echo "Platform: macOS (using Cocoa backend)"
    else
      export QT_QPA_PLATFORM="xcb"
      echo "Platform: Linux (using X11 backend)"
    fi
    echo ""

    # Optional: Create a virtual environment on first run
    if [ ! -d ".venv" ]; then
      echo "Creating virtual environment..."
      python -m venv .venv
      echo "Virtual environment created at .venv"
      echo "Activate it with: source .venv/bin/activate"
      echo ""
    fi
  '';
}
