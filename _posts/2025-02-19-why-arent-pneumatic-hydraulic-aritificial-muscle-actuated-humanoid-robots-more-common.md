---
layout: post
title: "Why aren't pneumatic/hydraulic artificial muscle actuated humanoid robots more common?"
date: 2025-02-19
description:
hidden: false
categories: []
tags:   []
---

This was a StackExchange question i asked many years ago [link](https://engineering.stackexchange.com/questions/49528/why-arent-pneumatic-hydraulic-artificial-muscle-actuated-humanoid-robots-more-c) and with Clone's showcase today it smells like musculoskeletal humanoid startups might be trending tomorrow. Pneumatic/hydraulic artificial muscles are attractive actuator units for several reasons:

- they're much cheaper than electric motors of comparable power output capability.

- instead of needing a high power darlington mosfet array for each motor, only one is needed for the prime movers. Small servo motors can individually control the pneumatic valves

- pneumatics are way easier to scale to hundreds of muscles than electric motors

- many pneumatic components can be prototyped with only a 3d printer; whereas custom motor design and fabrication for each joint is graduate school+ stuff

- hydraulic fluid (poor man's: water) can be used for muscles requiring high stiffness

I was having a really hard time looking past these advantages. Perhaps it was just not considered  possible to achieve precise pneumatic control in the past? but modern deep learning architectures could surely "learn" optimal control policies that give reasonable precision
Why haven't cheap (like <$1k) humanoid robots already been commercialized using pneumatic artificial muscles? In contrast, most of the DIY humanoid robot designs I saw involved big expensive motors, speed controller, and complex mechanical contraptions with orders of magnitude higher BOMs. But I wasn't even in college when I first realized how dramatic the differences  were so I just assumed there must be reasons why; I just couldn't see them. 
Anyway I eventually asked the world and got this answer from Tyler Habowski (I think [@Starstorms9](https://x.com/Starstorms9)?) If you are planning to imitate Clone's approach, think its worth considering his points:

> As cool as they seem, fluidic muscles like these are, unfortunately, not on track to be viable for mobile robotics for the foreseeable future. There are 3 primary issues:
> 
> Controls. It's somewhat easy to turn them on or off with solenoid valves, but a humanoid robot needs high precision to walk and manipulate objects beyond just on or off. And it turns out that actuating these fluidic muscles usefully is extremely challenging. Sticking a servo on a valve is a temptingly simple solution but has many issues. You have to direct the high pressure into the muscle at a precise rate to actuate it from the high pressure source and separately exhaust / recycle the low pressure fluid out also at a precise rate to relax it which requires at least 2 valves per muscle or a more complex multiway valve.
> 
> This is why after nearly a century of development in fluid controls, the best the industry has come up with are 'proportional pressure control valves' which are very complex and expensive (>$500 per valve, best case) and even then they are slow and inaccurate compared to motors and also hard to miniaturize.
> 
> The counterintuitive thing to understand here is that you need to control the pressure to an incredibly high precision to accomplish even the simplest tasks. As the robot interacts with objects and moves the actuators, their volumes and pressures will constantly be spiking and changing and keeping up with this requires a fast and accurate pressure control system. This is compounded by the fact that they are tension only actuators and need to be set up in antagonistic pairs (like human muscles) which requires precise and quick coordination between the opposing muscles.
> 
> All that is not to say it's impossible, it's just very expensive and complex.
> 
> Cost. It's true that the actuators themselves are cheap tubes but the rest of the system is very expensive. You need a high power compressor to pressurize the working fluid, pressure accumulators to smooth out high demand draws and accumulate expended working fluid to feed the pump, fluid distribution manifolds, pressure sensors, and most expensive of all, the pressure control valves.
> 
> The control valves are the killer here, a decade ago Festo built a prototype of what you're talking about called the 'Festo Air Arm' [1] which could even slowly write out large words. But this was realistically nothing more than a demonstration to show off their advanced proportional control valves. I can't find the source anymore but I remember seeing that each valve was ~$2k which seems sensible. No further development was done on this machine though.
> 
> On a related note, the Shadow Robot Company makes some of the most advanced humanoid hands available and they used to have a fluidic muscle version available but have since discontinued it because it was too expensive and difficult to control [2] [3]. Their current generation servo based hands are ~300k so it should give some idea of how tricky the pneumatic version was. A recent article about a college that adapted the pneumatic version of the hand put the total price for their pneumatic powered hand system at $350k [4].
> 
> Also of note are the pressure sensors. No amount of machine learning can control what it can't measure so you would need a sensor on each muscle which is not only hard to package but also very costly. I suspect >$10k bare minimum in total for a full robot even when mass produced. Trying to control it open loop style solely from the state of the valves would not be feasible either as it would be oblivious to the influence of outside forces acting on the joints. It needs to know if it needs to push harder through something or if it hit something and needs to relax.
> 
> Mechanical inefficiency. Regardless of the previous issues, this by itself is basically a dealbreaker for practical mobile robotics applications. Hydraulic systems are generally a little better than pneumatic, but given the large stack of components and high number of moving parts needed to implement these systems the total electrical efficiency is far below electric motors. While brushless motors with gearboxes can achieve >90% efficiency pneumatic systems are only ~10-20%, maybe up to 30% if you have really high quality (aka expensive) parts.
> 
> There is actually a Polish group attempting to do exactly what you're thinking of called Clone [5]. They've been working on it for several years now and have had some success building one arm but I'm very wary about their future prospects. If you look closely at their videos, you'll notice that they have only very coarse control of the joints that amounts to basically on or off, I have yet to see any fine controlled motion and I suspect that's due to the reasons I outlined earlier.
> 
> On a final note, despite what it may seem on first glance, fluidic muscles like these are actually fundamentally very different than human muscle. As a high level example, if you have an unpowered fluidic muscle robot you can't backdrive the actuators to move its limbs around freely because the pressure is locked up in the actuators. But biological muscle can be moved around without resistance. This points to the fact that fluidic muscles are actually position based actuators while biological muscles are force based. The pressure in the fluidic muscle directly corresponds to a position / length that it wants to be at whereas the chemical power in human muscle corresponds to an output force, regardless of position. This leads to some interesting high level controls tradeoffs and I believe there is good reason evolution chose the force based approach over position based.
> 
> All that said, I don't mean to discourage you if you want to pursue this! It's a fun idea and I think the current paradigm of forcibly adapting electric motors to power humanoid robots when they are so different than human muscle is an inherently flawed approach and that there must be a better way. I just think it's important to understand why fluid system engineering and fluidic muscles have been around for over half a century and no company has ever made a viable mobile robotics product with this technology.

So take this into consideration... personally, I beleive these points either aren't valid anymore or at least don't outweigh the benefits of hydrualic musculoskeletal humanoid actuation and I went ahead and tried to build [@HumanRobotsAI](https://x.com/HumanRobotsAI) Jan 2023--May 2024 and took a beak for reasons. There are lots of interesting problems in this domain and my analysis was that I could make a full-scale human-power humanoid for $526 (batch size 1k) but that had the inertia of a pre-COVID global economy priced in which is now evolving into something else. I still think it is possible to do it for <1k and I'm excited for any of y'all who try!  : )
