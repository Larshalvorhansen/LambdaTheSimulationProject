function Y = forecast_var(Y0,horizon,p)
    
    % Define and estimate the model
    mod=varm(size(Y0,2),p);
    var=estimate(mod,Y0(p+1:end,:),'Y0',Y0(1:p,:));
    
    % Forecast the model
    Y=forecast(var,horizon,Y0(end-p+1:end,:));
end