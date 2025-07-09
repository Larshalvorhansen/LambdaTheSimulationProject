function Y = simulate_arx(rate0,horizon,NumPaths,exo)
    
    % Set up model and estimate coefficients
    p = 1;
    q = 0;
    D = 0;
    offset=0;
    presample=3;
    Y0=rate0(offset+presample-p+1:offset+presample,:);
    rate0=rate0(offset+presample+1:end,:);
    exo=exo(offset+presample+1:end,:);
    
    % Define model according to minimum number of lags taken from above
    mod = arima(p,D,q);
    arx = estimate(mod,rate0,'Y0',Y0,'X',exo(1:length(rate0),:),'Display','off');
    
    % Simulate the model
    Y = simulate(arx,horizon,'X',exo(length(rate0)+1:length(rate0)+horizon,:),'NumPaths',NumPaths,'Y0',rate0);
    
end