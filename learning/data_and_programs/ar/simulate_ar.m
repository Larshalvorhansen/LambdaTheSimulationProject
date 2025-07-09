function Y = simulate_ar(rate0,horizon,NumPaths)
    
    % Set up model and estimate coefficients
    p = 1;
    q = 0;
    D = 0;
    offset=0;
    presample=3;
    Y0=rate0(offset+presample-p+1:offset+presample,:);
    rate0=rate0(offset+presample+1:end,:);
    
    % Define model according to minimum number of lags taken from above
    mod = arima(p,D,q);
    ar = estimate(mod,rate0,'Y0',Y0,'Display','off');
    
    % Simulate the model
    Y = simulate(ar,horizon,'NumPaths',NumPaths,'Y0',rate0);
    
end