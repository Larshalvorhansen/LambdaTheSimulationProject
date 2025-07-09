function Y = forecast_vecmx(Y0,horizon,X,p,r)
    
    % Define and estimate the model
    mod=vecm(size(Y0,2),r,p);
    vecx=estimate(mod,Y0(p+2:end,:),'Y0',Y0(1:p+1,:),'X',X(p+2:length(Y0),:));
    
    % Forecast the model
    Y=forecast(vecx,horizon,Y0(end-p:end,:),'X',X(length(Y0)+1:length(Y0)+horizon,:));
end